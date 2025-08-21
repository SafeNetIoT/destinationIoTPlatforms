from src.utils import *
from src.parsers.ip_extractor import process_pcap_ips
logger = logging.getLogger(__name__)

def translate_ip_to_domain(device_name: str, ips: set, ip_to_domain_map: dict) -> dict:
    """
    Translate IPs into domains using the IP-to-domain mappings.

    Args:
        device_name (str): The name of the device.
        ips (set): Set of IPs to translate.
        ip_to_domain_map (dict): Preloaded IP-to-domain mappings.

    Returns:
        dict: Translated IP-to-domain mapping for the device.
        float: Percentage of untranslated IPs.
    """
    translated_map = {}
    untranslated_ips = 0

    for ip in ips:
        if ip in ip_to_domain_map:
            translated_map[ip] = ip_to_domain_map[ip]
        else:
            untranslated_ips += 1

    percentage_untranslated = (untranslated_ips / len(ips)) * 100 if ips else 0
    # logger.info(f"Device {device_name}: {percentage_untranslated:.2f}% IPs could not be translated.")
    return translated_map, (percentage_untranslated, untranslated_ips, len(ips))

def compute_ip_to_domain(input_data:str, output_dir: str): #  sld:bool=False, ip_files:bool=False
    """
    Extract IPs from PCAP files

    Args:
        input_data (str): Either a file path with PCAP file paths
        output_dir (str): Directory to save the ip list results.
    """
   

    device_ips = defaultdict(list)
    device_pcap = defaultdict(list)
    ip_output_dir = os.path.join(output_dir, "ip_list")
    # os.makedirs(output_dir, exist_ok=True)
    os.makedirs(ip_output_dir, exist_ok=True)
    
    """
    # Parse input data
    if ip_files:   
        # load pre-computed IP files
        for ip_file in os.listdir(input_data):
            if not ip_file.endswith("_ips.json"):
                continue
            logger.info(f"Loading IPs from {input_data} {ip_file}")
            with open(os.path.join(input_data, ip_file), 'r') as f:
                device_ip_list = json.load(f)
                
            device_ips = device_ip_list
    
    else:
    """
    # if input data is a file with path to pcap files, extract IPs from them and convert to domains
    with open(input_data, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line.endswith(".pcap"):
                continue
            if not os.access(line, os.R_OK):
                logger.error(f"{line}: No read permission")
                continue

            device_name = get_device_name(line, dataset_root_path)
            device_pcap[device_name].append(line)
    
    # Extract IPs from PCAP files
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_pcap_ips, device_name, files): device_name for device_name, files in device_pcap.items()}
        for future in concurrent.futures.as_completed(futures):
            device_name = futures[future]
            try:
                ips = future.result()
                device_ips[device_name] = list(ips)
            except Exception as e:
                logger.error(f"Error processing device {device_name}: {e}")
    
    # Save intermediate IP results
    ip_file_path = os.path.join(ip_output_dir, "all_ips.json")
    with open(ip_file_path, 'w') as f:
        json.dump(device_ips, f, indent=4)
    logger.info(f"Extracted IPs from PCAP files and saved to {ip_file_path}")
    
    
    # all_translation_results = {}
    contacted_domains = {}
    all_untranslated_stats = {}

     # # Load IP-to-domain mappings
    ip_to_domain_dir = os.path.join(output_dir, 'domain_list')
    ip_to_domain_file = os.path.join(ip_to_domain_dir, "ip_domain_map.pkl")
    with open(ip_to_domain_file, 'rb') as f:
        ip_to_domain_map = pickle.load(f)
        
    # translate IPs to domains
    for device_name, ips in device_ips.items():
        translated_map, untranslated = translate_ip_to_domain(device_name, ips, ip_to_domain_map[device_name])
        # all_translation_results[device_name] = translated_map
        contacted_domains[device_name] = list(set(translated_map.values()))
        all_untranslated_stats[device_name] = list(untranslated)
    
    # Save results
    domain_output_dir = os.path.join(output_dir, "domain_list")
    save_contacted_domain(contacted_domains, domain_output_dir, False)
    save_untranslated_stats(all_untranslated_stats, ip_output_dir)
    
    # slds:
    ip_to_domain_file_sld = os.path.join(ip_to_domain_dir, "ip_sld_map.pkl")
    with open(ip_to_domain_file_sld, 'rb') as f:
        ip_to_domain_map_sld = pickle.load(f)
    contacted_domains_sld = {}
    for device_name, ips in device_ips.items():
        translated_map, untranslated = translate_ip_to_domain(device_name, ips, ip_to_domain_map_sld[device_name])
        contacted_domains_sld[device_name] = list(set(translated_map.values()))
    save_contacted_domain(contacted_domains_sld, domain_output_dir, True)
    
    logger.info("IP-to-domain translation completed and saved.")
    
    
def save_contacted_domain(results: dict, output_dir: str, sld:bool):
    """
    Save the IP-to-domain translation results to files.

    Args:
        results (dict): Mapping of devices to IP-to-domain mappings.
        output_dir (str): Directory to save the results.
    """
    os.makedirs(output_dir, exist_ok=True)
    if sld:
        file_name = "contacted_slds.json"
    else:
        file_name = "contacted_domains.json"
    with open(os.path.join(output_dir, file_name), 'w') as f:
        json.dump(results, f, indent=4)

def save_untranslated_stats(results: dict[list], output_dir: str):
    """
    Save the untranslated IP statistics.

    Args:
        results (dict): Mapping of devices to percentages of untranslated IPs.
        output_dir (str): Directory to save the results.
    """
    os.makedirs(output_dir, exist_ok=True)
    # save as csv file
    with open(os.path.join(output_dir, "_untranslated_ip_stats.csv"), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Device", "Percentage Untranslated", "Untranslated IPs", "Total IPs"])
        total_ip = 0
        total_untranslated = 0
        for device, stats in results.items():
            writer.writerow([device] + stats)
            total_untranslated += stats[1]
            total_ip += stats[2]
        writer.writerow(["Total", (total_untranslated / total_ip) * 100, total_untranslated, total_ip])
        
    # logger.info(f"Untranslated IP statistics saved to {output_dir}")