from src.utils import *
logger = logging.getLogger(__name__)

def extract_ips(in_pcap):
    """
    Extract all unique IP addresses from a PCAP file.
    """
    all_ips = set()

    # Use tshark to extract all IP addresses from the IP layer
    ip_lines = str(os.popen(f"tshark -r {in_pcap} -Y \"ip\" -T fields -e ip.src -e ip.dst").read()).splitlines()

    for line in ip_lines:
        line = line.split("\t")
        if len(line) < 2:
            continue
        src_ip = line[0]
        dst_ip = line[1]
        if not is_valid_ip(src_ip) or not is_valid_ip(dst_ip):
            continue
        if not is_local_address(src_ip):
            all_ips.add(src_ip)
        if not is_local_address(dst_ip):
            all_ips.add(dst_ip)
    return all_ips

def process_pcap_ips(device_name: str, pcap_files: list) -> set:
    """
    Extract all IPs from PCAP files for a single device.

    Args:
        device_name (str): The name of the device.
        pcap_files (list): List of PCAP file paths for the device.
        ip_output_dir (str): Directory to save intermediate IP results.

    Returns:
        set: All unique IPs found in the PCAP files for the device.
    """
    all_ips = set()
    logger.info(f"Extracting IPs for device: {device_name} from {len(pcap_files)} PCAP files.")

    for pcap_file in pcap_files:
        ips = extract_ips(pcap_file)
        all_ips.update(ips)

    # # Save intermediate IP results
    # ip_file_path = os.path.join(ip_output_dir, f"{device_name}_ips.txt")
    # os.makedirs(ip_output_dir, exist_ok=True)
    # with open(ip_file_path, 'w') as f:
    #     f.write("\n".join(sorted(all_ips)))
    # logger.info(f"Saved IPs for {device_name} to {ip_file_path}")

    return all_ips
