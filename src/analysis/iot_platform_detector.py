import json
import re
from collections import Counter
import argparse

def load_platform_signatures():
    """Load IoT platform signatures"""
    return {
        "AWS IoT Core": {
            "patterns": [r".*\.iot\..*\.amazonaws\.com", r".*\.ats\.iot\..*\.amazonaws\.com"],
            "domains": ["iot.amazonaws.com"],
            "ports": [8883, 443]
        },
        "Google Cloud IoT": {
            "patterns": [r"cloudiot\.googleapis\.com", r".*\.googleapis\.com"],
            "domains": ["cloudiot.googleapis.com"],
            "ports": [443, 8883]
        },
        "Tuya IoT": {
            "patterns": [r".*\.tuyaus\.com", r".*\.tuyaeu\.com", r".*\.tuyacn\.com"],
            "domains": ["a1.tuyaus.com", "a1.tuyaeu.com"],
            "ports": [443, 1883]
        },
        # Add more platforms from your OFFICIAL_PLATFORMS list
    }

def detect_iot_platforms(domains_file, ip_mappings_file):
    """Main IoT platform detection function"""
    
    # Load data
    with open(domains_file, 'r') as f:
        domains_data = json.load(f)
    
    with open(ip_mappings_file, 'r') as f:
        ip_data = json.load(f)
    
    platforms = load_platform_signatures()
    platform_scores = Counter()
    platform_evidence = {}
    
    # Analyze each device
    for device_name, domains in domains_data.items():
        device_platforms = Counter()
        device_evidence = {}
        
        for domain in domains:
            for platform_name, signature in platforms.items():
                # Check domain patterns
                for pattern in signature["patterns"]:
                    if re.match(pattern, domain):
                        device_platforms[platform_name] += 3  # Strong evidence
                        if platform_name not in device_evidence:
                            device_evidence[platform_name] = []
                        device_evidence[platform_name].append(domain)
                        break
                
                # Check exact domain matches
                if domain in signature.get("domains", []):
                    device_platforms[platform_name] += 5  # Very strong evidence
                    if platform_name not in device_evidence:
                        device_evidence[platform_name] = []
                    device_evidence[platform_name].append(domain)
        
        # Store results for this device
        platform_scores.update(device_platforms)
    
    # Generate final output in your specified format
    primary_platform = platform_scores.most_common(1)[0][0] if platform_scores else "Unknown"
    
    output = {
        "primary_platform": primary_platform,
        "platforms_detected": [
            {"platform": platform, "confidence": min(score/10, 1.0), "evidence": evidence}
            for platform, score in platform_scores.most_common(5)
        ],
        "platform_endpoints": platform_evidence
    }
    
    return output

def main():
    parser = argparse.ArgumentParser(description="Detect IoT platforms from domain data")
    parser.add_argument("--domain_file", required=True, help="Input domains JSON file")
    parser.add_argument("--ip_file", required=True, help="Input IP mappings JSON file") 
    parser.add_argument("--output", required=True, help="Output file for platform results")
    
    args = parser.parse_args()
    
    results = detect_iot_platforms(args.domain_file, args.ip_file)
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"IoT platform detection completed. Results saved to {args.output}")
    print(f"Primary platform: {results['primary_platform']}")

if __name__ == "__main__":
    main()
