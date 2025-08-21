#!bin/bash

# Destination Analysis - Run

## First step: extract domain-ip mappings and get domain list from DNS/TLS data
python3 destination_analysis.py domains --input_file /home/hutr/iot-longitudinal/input_files/all_devices_remove_duplicates/input_2019idle.txt --output_dir /home/hutr/iot-longitudinal/output_destination/all_devices_remove_duplicates/2019idle  --exp 2019idle

# or run.sh 

## Second step: extract destination IPs and get destination list from domain-ip mappings
python3 destination_analysis.py map_ips --input_file /home/hutr/iot-longitudinal/input_files/all_devices_remove_duplicates/input_2019idle.txt --output_dir /home/hutr/iot-longitudinal/output_destination/all_devices_remove_duplicates/2019idle  --exp 2019idle

## Third step mapping ip to domain using DNS/TLS data from uncontrolled dataset
python3 scripts/ip_to_domain/ip_to_domain_with_uncontrolled_dns.py

