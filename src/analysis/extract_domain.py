from multiprocessing import Pool
from src.parsers.dns_tls_extractor import extract_domains, extract_sld
from src.utils import *

logger = logging.getLogger(__name__)
logging.getLogger("tldextract").setLevel(logging.CRITICAL)
logging.getLogger("filelock").setLevel(logging.WARNING)

def process_pcap(device:str, pcap_files:list)->set[str]:
    """Process a single PCAP file to extract domains."""
    unique_slds, domain_list, ip_sld_map, ip_domain_map = set(), set(), {}, {}
    domain_sld_map = {}
    logger.info(f"Processing device: {device} with {len(pcap_files)} PCAP files.")
    for pcap_file in pcap_files:
        domain_list_cur, ip_domain_map_cur = extract_domains(pcap_file)
        for domain in domain_list_cur:
            tmp_sld = extract_sld(domain)
            unique_slds.add(tmp_sld)
            domain_sld_map[domain] = tmp_sld
        domain_list.update(domain_list_cur)
        for ip, domain in ip_domain_map_cur.items():
            ip_domain_map[ip] = domain
            ip_sld_map[ip] = domain_sld_map.get(domain, None)
    return unique_slds, domain_list, ip_sld_map, ip_domain_map


def compute_unique_domains(input_file, output_dir):
    """Compute unique domains for all PCAPs in a directory using multiprocessing."""
    dict_dec = defaultdict(list)
    with open(input_file, 'r') as f:
        f = f.readlines()
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line.endswith(".pcap"):
                continue
            if not os.access(line, os.R_OK):
                logger.error(f"{line}: No read permission")
                continue
            
            # Extract the device name from the pcap file name
            device_name = get_device_name(line, dataset_root_path)
            dict_dec[device_name].append(line)
            
    all_slds, ip_sld_map_all, all_domains, ip_domain_map_all = {}, {}, {}, {}
    
    # print(dict_dec)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_dev = {executor.submit(process_pcap, device_name, dict_dec[device_name]): device_name for device_name in dict_dec.keys()}
        for future in concurrent.futures.as_completed(future_to_dev):
            device_name = future_to_dev[future]
            result = future.result()
            if result == None:
                continue
            try:
                unique_slds, domain_list, sld_ip_map, domain_ip_map = result
                all_slds[device_name] = list(unique_slds)
                ip_sld_map_all[device_name] = sld_ip_map
                all_domains[device_name] = list(domain_list)
                ip_domain_map_all[device_name] = domain_ip_map
            except Exception as e:
                logger.error(f"Error processing device {device_name}: {e}")
    logger.info("IP-Domain Mapping Extracted... Saving results")
    # Save the results
    domain_output_dir = os.path.join(output_dir, 'domain_list')
    save_domains(all_slds, domain_output_dir, "unique_slds")
    save_domains(all_domains, domain_output_dir, "unique_domains")
    save_domains(ip_sld_map_all, domain_output_dir, "ip_sld_map", pickle_flag=True)
    save_domains(ip_domain_map_all, domain_output_dir, "ip_domain_map", pickle_flag=True)
    logger.info("Unique domains computed and saved.")

def save_domains(results:dict, output_dir:str, file_name:str, pickle_flag=False):
    """Save the results to a file."""
    if not os.path.exists(output_dir):
        os.system(f'mkdir -pv {output_dir}')
    if pickle_flag:
        with open(os.path.join(output_dir, f"{file_name}.pkl"), 'wb') as f:
            pickle.dump(results, f)
    else:
        with open(os.path.join(output_dir, f"{file_name}.json"), 'w') as f:
            json.dump(results, f, indent=4)
    logger.info(f"{file_name} saved to {output_dir}")
                