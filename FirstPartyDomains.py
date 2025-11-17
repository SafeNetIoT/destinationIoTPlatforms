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
    parser = argparse.ArgumentParser(description="Generate first-party domains for a manufacturer")
    parser.add_argument("--manufacturer", required=True, help="Manufacturer name (e.g., Sonos, Amazon)")
    parser.add_argument("--output", required=True, help="Output file path")
    
    args = parser.parse_args()
    
    # Get domains for the manufacturer
    first_party_domains = get_first_party_domains(args.manufacturer)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Write to file
    with open(args.output, "w") as f:
        for domain in first_party_domains:
            f.write(domain + "\n")
    
    print(f"First-party domains for {args.manufacturer} saved to {args.output}")
    print(f"Domains: {', '.join(first_party_domains)}")

if __name__ == "__main__":
    main()
