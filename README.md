#EXTRACTING AND CLASSIFYING DESTINATIONS 

Examines where IoT devices send their data by extracting DNS/TLS destinations from PCAP files, mapping IPs to domains, identifying cloud and platform dependencies, and classifying traffic as first-party, support-party, third-party, or platform-party over time (monthly longitudinal analysis).

This pipeline works for any IoT device as long as PCAPs follow the format: YYYY-MM-DD_HH.MM.SS_<deviceIP>.pcap

and are stored under: /data/disk1/traffic/by-name/<device>/ctrl2/



**1. Input Files (Per-Month Longitudinal Setup)**
Generate a monthly list of PCAP files.
The pipeline groups files by filename pattern: YYYY-MM-*.pcap

Example command (automated inside run_longitudinal.sh):

```
find /data/disk1/traffic/by-name/<device>/ctrl2 \
    -type f -name "2025-07-*.pcap" \
    > inputs/<device>_longitudinal/2025/Jul_2025.txt
```
Running the provided script:
```
./run_longitudinal.sh
```

This automatically creates all per-month input lists for all years you specify.


**2. Get Domain-to-IP Mappings (Per Month)**
Extract domain-to-IP mappings from DNS queries and TLS handshakes for each month:

```
python3 destination_analysis.py domains \
    --input_file inputs/<device>_longitudinal/<year>/<Mon_Year>.txt \
    --output_dir analysis_longitudinal/<device>/<year>/<Mon_Year> \
    --exp <device>_domains
```
Output written to:
analysis_longitudinal/<device>/<year>/<Mon_Year>/domain_list/
    contacted_domains.json
    unique_domains.json


**3. Extract IPs & Derive IP→Domain Map (Per Month)**
```
python3 destination_analysis.py map_ips \
    --input_file inputs/<device>_longitudinal/<year>/<Mon_Year>.txt \
    --output_dir analysis_longitudinal/<device>/<year>/<Mon_Year> \
    --exp <device>_ipmap
```   
Output:
analysis_longitudinal/<device>/<year>/<Mon_Year>/ip_list/
    all_ips.json
    ip_domain_map.pkl   (organization data may be empty initially)

If ip_domain_map.pkl is missing (new device / new month), initialize empty files:
python3 init_empty_ip_maps.py <device> <year1> <year2> ...
This ensures later steps run without interruption.


**4. Organizational Attribution (Optional but Recommended)**
Organizational lookup can be added manually or automated later.
You may also enrich ip_domain_map.pkl using the notebooks in:
scripts/getorg/


5**. Longitudinal Traffic Classification (First / Support / Third / Platform)**
The enhanced classifier (party.py) categorizes every contacted domain per month.
Run:
```
python3 party.py \
    --device <device> \
    --years <year1> <year2> ... \
    --base_dir analysis_longitudinal
```
Output:
analysis_longitudinal/<device>/categorized_domains_Jul_2025.csv
analysis_longitudinal/<device>/categorized_domains_Aug_2025.csv
...

To generate first-party reference lists:
```
python3 FirstPartyDomains.py \
    --manufacturer "Sonos" \
    --output analysis/<device>/first_party_domains.txt
```


**6. IP Geolocation**
```
python3 geolocate_ips.py \
    --input analysis_longitudinal/<device>/<year>/<Mon_Year>/ip_list/all_ips.json \
    --output analysis_longitudinal/<device>/<year>/<Mon_Year>/geolocation.json \
    --db GeoLite2-Country.mmdb
```
Output example:
{
  "23.194.10.201": {
    "country_iso_code": "IE",
    "country_name": "Ireland"
  }
}



**7. Using the Pipeline for ANY New Device**
For a device named <new_device>:
Ensure PCAPs live in:
/data/disk1/traffic/by-name/<new_device>/ctrl2/

Edit the following at the top of run_longitudinal.sh:
DEVICE_NAME="<new_device>"
YEARS="2023 2024 2025"

Run the entire extraction:
```
./run_longitudinal.sh
```
Initialize empty organization maps:
```
python3 init_empty_ip_maps.py <new_device> 2023 2024 2025
```
Categorize:
```
python3 party.py \
    --device <new_device> \
    --years 2023 2024 2025
```
All outputs will appear in:
analysis_longitudinal/<new_device>/


**8. Summary of All Outputs**
Domain Extraction (per month)
analysis_longitudinal/<device>/<year>/<Mon_Year>/domain_list/
    contacted_domains.json
    unique_domains.json

IP Extraction (per month)
analysis_longitudinal/<device>/<year>/<Mon_Year>/ip_list/
    all_ips.json
    ip_domain_map.pkl

Monthly Domain Categorisation
analysis_longitudinal/<device>/categorized_domains_<Mon>_<Year>.csv

Optional Geolocation
geolocation.json

Final Output Example (Monthly CSV)
Month-Year,Domain,SLD,TLD,Category,Organization,Query Type
Jul-2025,conn-i-078cd5...ws.sonos.com,sonos,com,First-party,Sonos Inc,A
Jul-2025,s3.amazonaws.com,amazonaws.com,com,Support-party,Amazon AWS,A
Jul-2025,cloudfront.net,cloudfront,net,Support-party,Amazon AWS,A
Jul-2025,metrics.sonos.com,sonos,com,First-party,Sonos Inc,A
