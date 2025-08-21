import os

# Define the MAC address
MAC_ADDRESS = "9c:9c:1f:91:e1:b6"

# Base directory
BASE_DIR = os.path.expanduser("~/snap/snapd-desktop-integration/current/Documents/Appliance")
MAC_DIR = os.path.join(BASE_DIR, MAC_ADDRESS)

# First-party output file
FIRST_PARTY_FILE = os.path.join(MAC_DIR, "first_party_domains.txt")

# First-party domains
FIRST_PARTY_DOMAINS = ["vesync.com",
"ntp.vesync.com",
"vdmpmqtt.vesync.com"]

# Ensure the MAC directory exists
if not os.path.exists(MAC_DIR):
    print(f"Error: Directory {MAC_DIR} not found.")
else:
    # Write first-party domains to the file
    with open(FIRST_PARTY_FILE, "w") as f:
        for domain in FIRST_PARTY_DOMAINS:
            f.write(domain + "\n")
    print(f"First-party domains saved to {FIRST_PARTY_FILE}")
