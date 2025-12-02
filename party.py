import os
import json
import pickle
import csv
import subprocess
import ipaddress
import tldextract
import argparse
from collections import defaultdict


def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def get_whois_data(domain):
    try:
        result = subprocess.run(
            ['whois', domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=10
        )
        return result.stdout.decode(errors="ignore")
    except Exception:
        return None


def extract_organization(whois_data):
    if whois_data:
        for line in whois_data.split('\n'):
            if 'Organization' in line or 'OrgName' in line:
                try:
                    return line.split(':', 1)[1].strip()
                except Exception:
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


def categorize_domains(contacted_domains, unique_domains, ip_map, first_party_suffixes=None):
    """
    contacted_domains: list of domains contacted in that month
    unique_domains: list of domains considered first-party in the original pipeline
                    (may now be all domains depending on upstream processing)
    ip_map: domain -> {organization, query_type, ...}
    first_party_suffixes: optional list of domain suffixes from first_party_domains.txt
                          e.g. ['sonos.com', 'sonos.net', 'vesync.com']
    """
    support_party_list = ['aws', 'cloudflare', 'akamai', 'fastly', 'cdn', 'dns', 'digicert']

    unique_set = set(unique_domains) 
    
    # unique_domains should be a list; normalize safely:
    if isinstance(unique_domains, (list, set)):
        unique_set = set(unique_domains)
    else:
        unique_set = set()

    fp_suffixes = [s.lower() for s in (first_party_suffixes or [])]

    categorized_data = []

    for domain in contacted_domains:
        sld, tld = extract_sld_tld(domain)
        d_lower = domain.lower()

        # Original logic: domain is first-party if it is in unique_domains
        is_first = domain in unique_set

        # Extended logic: also treat anything ending with a known first-party suffix as first-party
        if not is_first and fp_suffixes:
            if any(d_lower.endswith(suf) for suf in fp_suffixes):
                is_first = True

        category = "First-party" if is_first else "Third-party"

        org = ip_map.get(domain, {}).get("organization", "Unknown")
        query_type = ip_map.get(domain, {}).get("query_type", "Unknown")

        # If organization is unknown, try WHOIS
        if org == "Unknown":
            whois_data = get_whois_data(domain)
            extracted_org = extract_organization(whois_data)
            if extracted_org != "Unknown":
                org = extracted_org

        # Support-party override based on org name
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
    parser = argparse.ArgumentParser(
        description="Categorize domains (First/Support/Third) longitudinally per device"
    )
    parser.add_argument("--device", required=True,
                        help="Device name (matches folder under analysis_longitudinal/)")
    parser.add_argument("--base_dir", default="analysis_longitudinal",
                        help="Base directory for longitudinal analysis (default: analysis_longitudinal)")
    parser.add_argument("--years", nargs="+", default=["2023", "2024", "2025"],
                        help="Years to process, e.g. --years 2024 2025")
    args = parser.parse_args()

    # Base path for this device's longitudinal results
    base_path = os.path.join(os.path.expanduser(args.base_dir), args.device)
    output_base_path = base_path  # CSVs go alongside analysis

    # Optional: per-device first-party domain suffixes
    # Expected file: analysis/<device>/first_party_domains.txt
    first_party_file = os.path.join("analysis", args.device, "first_party_domains.txt")
    first_party_suffixes = []
    if os.path.exists(first_party_file):
        with open(first_party_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    first_party_suffixes.append(line.lower())
        print(f"Loaded {len(first_party_suffixes)} first-party suffixes from {first_party_file}")
    else:
        print(f"No first-party domain file found at {first_party_file}; using unique_domains only")

    years = args.years
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for year in years:
        for month in months:
            month_folder = f"{month}_{year}"
            folder_path = os.path.join(base_path, year, month_folder)
            output_csv = os.path.join(output_base_path, f"categorized_domains_{month}_{year}.csv")

            if not os.path.exists(folder_path):
                continue

            domain_list_path = os.path.join(folder_path, "domain_list")

            contacted_domains_file = os.path.join(domain_list_path, "contacted_domains.json")
            unique_domains_file = os.path.join(domain_list_path, "unique_domains.json")
            ip_map_file = os.path.join(domain_list_path, "ip_domain_map.pkl")

            if not (os.path.exists(contacted_domains_file)
                    and os.path.exists(unique_domains_file)
                    and os.path.exists(ip_map_file)):
                continue

            # Load raw data
            contacted_raw = load_json(contacted_domains_file)
            unique_raw = load_json(unique_domains_file)
            ip_map = load_pickle(ip_map_file)

            # Normalise contacted_domains: list or dict {"..": [list]}
            if isinstance(contacted_raw, dict):
                tmp = []
                for v in contacted_raw.values():
                    if isinstance(v, list):
                        tmp.extend(v)
                contacted_domains = sorted(set(tmp))
            else:
                contacted_domains = contacted_raw

            # Normalise unique_domains similarly
            if isinstance(unique_raw, dict):
                # If it looks like the newer "{ '..': [list of all domains] }" shape,
                # DO NOT treat this as a curated first-party list.
                if ".." in unique_raw and isinstance(unique_raw[".."], list):
                    unique_domains = []  # no special first-party info here
                else:
                    unique_domains = list(unique_raw.keys())
            else:
                unique_domains = unique_raw


            categorized_data = categorize_domains(
                contacted_domains,
                unique_domains,
                ip_map,
                first_party_suffixes=first_party_suffixes
            )

            for entry in categorized_data:
                entry.insert(0, f"{month}-{year}")

            save_to_csv(categorized_data, output_csv)
            print(f"Categorized domain data saved to {output_csv}")


if __name__ == "__main__":
    main()
