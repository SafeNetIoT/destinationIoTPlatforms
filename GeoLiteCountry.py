import socket
import csv
import geoip2.database
import requests
import pandas as pd

# Paths to GeoIP databases (update with actual paths)
GEOIP_COUNTRY_DB = "Path to GeoLite2-Country.mmdb file"
GEOIP_ASN_DB = "Path to GeoLite2-ASN.mmdb file"

# Input file paths
FILE1 = "Path to organisation file in .csv format"
FILE2 = "Path to IP to SLD mapping file in .csv format"

# Output file
OUTPUT_FILE = "Path to output file in .csv format"

# RIPE API URL
RIPE_API_URL = "https://stat.ripe.net/data/prefix-overview/data.json?resource={}"

def get_geoip_info(ip):
    """Fetch country and ASN info for an IP using GeoIP databases."""
    country, asn, org = None, None, None

    try:
        with geoip2.database.Reader(GEOIP_COUNTRY_DB) as country_reader:
            country = country_reader.country(ip).country.name
    except (geoip2.errors.AddressNotFoundError, FileNotFoundError):
        country = None

    try:
        with geoip2.database.Reader(GEOIP_ASN_DB) as asn_reader:
            asn_data = asn_reader.asn(ip)
            asn = asn_data.autonomous_system_number
            org = asn_data.autonomous_system_organization
    except (geoip2.errors.AddressNotFoundError, FileNotFoundError):
        asn, org = None, None

    # If local lookup fails, use RIPEstat API
    if not country or not asn or not org:
        country, asn, org = get_ripe_info(ip)

    return country or "Unknown", asn or "Unknown", org or "Unknown"

def get_ripe_info(ip):
    """Fetch country, ASN, and organization using RIPEstat API."""
    try:
        response = requests.get(RIPE_API_URL.format(ip))
        data = response.json()

        asn = data["data"]["asns"][0]["asn"] if data["data"]["asns"] else None
        org = data["data"]["asns"][0]["holder"] if data["data"]["asns"] else None
        country = data["data"]["located_resources"][0]["location"]["country"] if "located_resources" in data["data"] else None

        return country, asn, org
    except Exception as e:
        print(f"[!] RIPE API error for IP {ip}: {e}")
        return None, None, None

# Load both CSV files
df1 = pd.read_csv(FILE1)
df2 = pd.read_csv(FILE2)

# Ensure proper column names
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

# Create a mapping from SLD to first IP Address
ip_lookup = df2.groupby("SLD")["IP Address"].first().to_dict()

# Update unknown values using IP lookup
for index, row in df1.iterrows():
    if row["Country"] == "Unknown" or row["ASN Number"] == "Unknown" or row["Organization"] == "Unknown":
        sld = row["SLD"]
        if sld in ip_lookup:
            ip = ip_lookup[sld]
            country, asn, org = get_geoip_info(ip)
            df1.at[index, "Country"] = country
            df1.at[index, "ASN Number"] = asn
            df1.at[index, "Organization"] = org

# Save the final CSV
df1.to_csv(OUTPUT_FILE, index=False)

print(f"Processing complete! Enriched data saved to {OUTPUT_FILE}")
