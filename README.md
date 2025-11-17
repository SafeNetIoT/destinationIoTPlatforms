# Destination Analysis of IoT Traffic -- edited to specifically extract IoT platforms

Examines where IoT devices send their data, by mapping cloud endpoints, identifying server ownership, and classifying traffic as first-party, support, or third-party across regions and timelines.

## 1. Input files
First, generate a list of file paths for the PCAP files in your dataset. Use the following command:
```
find /your-dataset-path > inputs/{year}/xxx.txt 
```
## 2. Get domain to IP mappings
Extract domain-to-IP mappings from DNS queries and TLS handshakes:
```
python3 destination_analysis.py domains --input_file /inputs/{year}/xxx.txt --output_dir /your_output_dir  --exp your_exp_name_for_logging
```
## 3. Map IPs to Domains & Detect IoT Platforms
Extract all destination IPs and identify IoT platform usage:
```
python3 destination_analysis.py map_ips --input_file /inputs/{year}/xxx.txt --output_dir /your_output_dir --exp your_exp_name_for_logging
python3 iot_platform_detector.py --domain_file analysis/sonos_one/domains.json --ip_file analysis/sonos_one/ip_mappings.json --output analysis/sonos_one/platforms_detected.json
```

## 4. Organizational Attribution & Platform Validation
Run ipynb files from `scripts/getorg/
```
# NEW: Automated organizational resolution
python3 destination_analysis.py resolve_orgs --domain_file analysis/sonos_one/domains.txt --output_file analysis/sonos_one/organizations.json --exp sonos_orgs
```

## 5. Traffic Classification & Geographic Analysis
Classify traffic with enhanced platform-party category:
First-party: Device manufacturer domains (sonos.com, sonos.net)

Platform-party: IoT infrastructure providers (AWS IoT Core, Tuya Cloud)

Support-party: CDNs, analytics, operational services

Third-party: Advertising, tracking, external services

```
# Enhanced classification including platform-party
python3 party.py --platform_file analysis/sonos_one/platforms_detected.json --output analysis/sonos_one/classification.json

# Generate first-party domains list
python3 FirstPartyDomains.py --manufacturer "Sonos" --output analysis/sonos_one/first_party_domains.txt
```
## 6. Geographic Analysis & Reporting

```
# IP geolocation
python3 GeoLiteCountry.py --input analysis/sonos_one/ip_mappings.json --output analysis/sonos_one/geolocation.json

# Generate comprehensive platform report
python3 iot_platform_report.py --device sonos_one --output reports/sonos_platform_analysis.pdf

```
