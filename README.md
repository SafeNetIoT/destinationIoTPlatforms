# Destination Analysis

`tshark version 4.2.2`

## 1. Input files
First, generate a list of file paths for the PCAP files in your dataset. Use the following command:
```
find /your-dataset-path > inputs/{year}/xxx.txt 
```
## 2. Get domain to IP mappings
Second, get domain to IP mappings from DNS and TLS handshakes in PCAP files.
```
python3 destination_analysis.py domains --input_file /inputs/{year}/xxx.txt --output_dir /your_output_dir  --exp your_exp_name_for_logging
```
## 3. Get list of IPs and translate them into domains
Get list of IPs from PCAP files. Use the domain-to-ip mappings from last step to translate IPs to domains. Then, we get the list of contacted destination domains by devices. 
```
python3 destination_analysis.py map_ips --input_file /inputs/{year}/xxx.txt --output_dir /your_output_dir --exp your_exp_name_for_logging
```
### Optional: if already have domain to IP mappings from uncontrolled datasets. Skip step 2. 
Run step 3 destiantion_analysis.py to get the list of IPs. 
Then, run `python3 scripts/ip_to_domain/ip_to_domain_with_uncontrolled_dns.py` to translate IPs to domains 


## 4. Get Domain Orgnazation 
Run ipynb files from `scripts/getorg/`
`getorg.ipynb` is the working version. `getorg_2025Jan.ipynb` is the clean version

## 5. IP Geo location (still working on it)
`scripts/ip-geo/`