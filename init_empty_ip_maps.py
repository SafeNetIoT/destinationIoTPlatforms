import os
import sys
import pickle

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 init_empty_ip_maps.py <DEVICE_NAME> <YEAR1> [YEAR2 ...]")
        sys.exit(1)

    device = sys.argv[1]
    years = sys.argv[2:]

    base = os.path.join("analysis_longitudinal", device)

    for year in years:
        year_dir = os.path.join(base, year)
        if not os.path.isdir(year_dir):
            continue

        for month_folder in os.listdir(year_dir):
            domain_list_path = os.path.join(year_dir, month_folder, "domain_list")
            if not os.path.isdir(domain_list_path):
                continue

            pkl_path = os.path.join(domain_list_path, "ip_domain_map.pkl")
            if os.path.exists(pkl_path):
                continue

            os.makedirs(domain_list_path, exist_ok=True)
            with open(pkl_path, "wb") as f:
                pickle.dump({}, f)

            print(f"Created empty {pkl_path}")

if __name__ == "__main__":
    main()
