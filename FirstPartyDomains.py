import os
import argparse
import json

def get_first_party_domains(manufacturer):
    """Get first-party domains based on manufacturer"""
    manufacturer_domains = {
        "Sonos": ["sonos.com", "sonos.net", "sonosapi.com"],
        "Amazon": ["amazon.com", "amazonalexa.com", "alexa.com"],
        "Google": ["google.com", "googleapis.com", "gstatic.com", "nest.com"],
        "Tuya": ["tuya.com", "tuyaus.com", "tuyaeu.com", "tuyacn.com"],
        "Ring": ["ring.com", "ringapis.com"],
        "Wyze": ["wyze.com", "wzconnect.com"],
        # Add more manufacturers as needed
    }
    return manufacturer_domains.get(manufacturer, [])

def main():
    parser = argparse.ArgumentParser(description="Categorize domains (First/Third/Support) longitudinally")
    parser.add_argument("--device", required=True, help="Device name (matches folder under analysis_longitudinal/)")
    parser.add_argument("--base_dir", default="analysis_longitudinal", help="Base directory for longitudinal analysis")
    parser.add_argument("--years", nargs="+", default=["2023", "2024", "2025"], help="Years to process")
    args = parser.parse_args()

    base_path = os.path.join(os.path.expanduser(args.base_dir), args.device)
    output_base_path = base_path

    # NEW: Try to load per-device first_party_domains.txt from analysis/<device>/
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
        print(f"No first-party domain file found at {first_party_file}; falling back to unique_domains only")

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
            unique_domains_file    = os.path.join(domain_list_path, "unique_domains.json")
            ip_map_file            = os.path.join(domain_list_path, "ip_domain_map.pkl")

            if not (os.path.exists(contacted_domains_file) and
                    os.path.exists(unique_domains_file) and
                    os.path.exists(ip_map_file)):
                continue

            # Load and normalise JSON shapes (list vs {"..": [...]})
            contacted_raw = load_json(contacted_domains_file)
            unique_raw    = load_json(unique_domains_file)
            ip_map        = load_pickle(ip_map_file)

            # contacted_domains: flat list
            if isinstance(contacted_raw, dict):
                tmp = []
                for v in contacted_raw.values():
                    if isinstance(v, list):
                        tmp.extend(v)
                contacted_domains = sorted(set(tmp))
            else:
                contacted_domains = contacted_raw

            # unique_domains: either list or dict->keys
            if isinstance(unique_raw, dict):
                # If in your data unique_raw looks like {"..": [domains]}, flatten it
                if ".." in unique_raw and isinstance(unique_raw[".."], list):
                    unique_domains = unique_raw[".."]
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
