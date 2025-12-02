import argparse
import json
import ipaddress
import geoip2.database
from geoip2.errors import AddressNotFoundError

def load_ips(path):
    """Load IPs from JSON that may be:
       - a list of IP strings, or
       - a dict of {key: [ip1, ip2, ...]}, e.g. {"..": [ ... ]}
    """
    with open(path, "r") as f:
        data = json.load(f)

    ips = set()

    if isinstance(data, list):
        # Simple case: ["1.2.3.4", "5.6.7.8", ...]
        for item in data:
            if isinstance(item, str):
                ips.add(item)
    elif isinstance(data, dict):
        # Dict case: { "..": [ "1.2.3.4", ... ], "other": [ ... ] }
        for value in data.values():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        ips.add(item)
    else:
        # Unexpected format; nothing to do
        return []

    return sorted(ips)

def main():
    parser = argparse.ArgumentParser(description="Geolocate IPs using GeoLite2 Country DB")
    parser.add_argument("--input", required=True, help="Path to JSON file containing IPs")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument("--db", required=True, help="Path to GeoLite2-Country.mmdb")
    args = parser.parse_args()

    ips = load_ips(args.input)
    print(f"Loaded {len(ips)} unique candidate IPs")

    geodata = {}
    reader = geoip2.database.Reader(args.db)

    for ip in ips:
        # Skip anything that isn't a valid IPv4/IPv6 string
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            continue

        try:
            resp = reader.country(ip)
            geodata[ip] = {
                "country_iso_code": resp.country.iso_code,
                "country_name": resp.country.name,
            }
        except AddressNotFoundError:
            # Private / local IP or not in DB
            continue
        except Exception as e:
            print(f"Error looking up {ip}: {e}")

    reader.close()

    with open(args.output, "w") as f:
        json.dump(geodata, f, indent=2)

    print(f"Wrote geolocation for {len(geodata)} IPs to {args.output}")

if __name__ == "__main__":
    main()
