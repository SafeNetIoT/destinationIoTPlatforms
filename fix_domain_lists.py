import os
import json
import argparse

def normalize(path):
    with open(path, "r") as f:
        data = json.load(f)

    # If already correct format (list)
    if isinstance(data, list):
        return False

    # If format is { "..": [list] }
    if isinstance(data, dict) and ".." in data:
        cleaned = data[".."]
        with open(path, "w") as f:
            json.dump(cleaned, f, indent=4)
        return True

    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", required=True)
    parser.add_argument("--base_dir", default="analysis_longitudinal")
    args = parser.parse_args()

    base = f"{args.base_dir}/{args.device}"

    for root, dirs, files in os.walk(base):
        for fname in ("unique_domains.json", "contacted_domains.json"):
            fullpath = os.path.join(root, fname)
            if os.path.exists(fullpath):
                changed = normalize(fullpath)
                if changed:
                    print(f"Normalized {fullpath}")

if __name__ == "__main__":
    main()
