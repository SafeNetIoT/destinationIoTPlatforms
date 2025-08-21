import os
import json
import pickle
import csv
import subprocess
import ipaddress
import tldextract
from collections import defaultdict


def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def get_whois_data(domain):
    try:
        result = subprocess.run(['whois', domain], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return result.stdout.decode()
    except:
        return None


def extract_organization(whois_data):
    if whois_data:
        for line in whois_data.split('\n'):
            if 'Organization' in line or 'OrgName' in line:
                try:
                    return line.split(':')[1].strip()
                except:
                    continue
    return "Unknown"


def is_local_address(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_multicast or ip.is_reserved or ip.is_loopback
    except ValueError:
        return False


def extract_sld_tld(domain):
    ext = tldextract.extract(domain)
    return ext.domain, ext.suffix


def categorize_domains(contacted_domains, unique_domains, ip_map):
    support_party_list = ['aws', 'cloudflare', 'akamai', 'fastly', 'cdn', 'dns', 'digicert']
    categorized_data = []
    for domain in contacted_domains:
        sld, tld = extract_sld_tld(domain)
        category = "First-party" if domain in unique_domains else "Third-party"
        org = ip_map.get(domain, {}).get("organization", "Unknown")
        query_type = ip_map.get(domain, {}).get("query_type", "Unknown")

        if org == "Unknown":
            whois_data = get_whois_data(domain)
            org = extract_organization(whois_data)

        for s in support_party_list:
            if s in org.lower():
                category = "Support-party"
                break

        categorized_data.append([domain, sld, tld, category, org, query_type])
    return categorized_data


def save_to_csv(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Month-Year", "Domain", "SLD", "TLD", "Category", "Organization", "Query Type"])
        writer.writerows(data)


def main():
    base_path = os.path.expanduser("~/snap/snapd-desktop-integration/current/Documents/Appliance/8:e9:f6:2a:2e:a2")
    output_base_path = os.path.expanduser("~/snap/snapd-desktop-integration/current/Documents/categorized_domains")

    years = ['2023', '2024', '2025']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for year in years:
        for month in months:
            month_folder = f"{month}_{year}"
            folder_path = os.path.join(base_path, year, month_folder)
            output_csv = os.path.join(output_base_path, f"categorized_domains_{month}_{year}.csv")

            if not os.path.exists(folder_path):
                continue

            domain_list_path = os.path.join(folder_path, "domain_list")
            ip_list_path = os.path.join(folder_path, "ip_list")

            contacted_domains_file = os.path.join(domain_list_path, "contacted_domains.json")
            unique_domains_file = os.path.join(domain_list_path, "unique_domains.json")
            ip_map_file = os.path.join(domain_list_path, "ip_domain_map.pkl")

            if not os.path.exists(contacted_domains_file) or not os.path.exists(
                    unique_domains_file) or not os.path.exists(ip_map_file):
                continue

            contacted_domains = load_json(contacted_domains_file)
            unique_domains = load_json(unique_domains_file)
            ip_map = load_pickle(ip_map_file)

            categorized_data = categorize_domains(contacted_domains, unique_domains, ip_map)
            for entry in categorized_data:
                entry.insert(0, f"{month}-{year}")

            save_to_csv(categorized_data, output_csv)
            print(f"Categorized domain data saved to {output_csv}")


if __name__ == "__main__":
    main()
