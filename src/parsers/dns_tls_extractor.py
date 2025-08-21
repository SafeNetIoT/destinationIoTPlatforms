from src.utils import *
logger = logging.getLogger(__name__)

def extract_sld(domain):
    # no_fetch_extract = tldextract.TLDExtract(suffix_list_urls=("https://raw.github.com/mozilla/gecko-dev/master/netwerk/dns/effective_tld_names.dat"))
    # no_cache_extract = tldextract.TLDExtract(cache_dir=False)
    ext = tldextract.extract(domain)
    # ext = no_cache_extract(domain)
    # if ext.suffix is None:
    #     return None
    return f"{ext.domain}.{ext.suffix}"

def extract_domains(pcap_file:str)->tuple[set[str], set[str], dict[str, str], dict[str, str]]:
    # unique_slds = set()
    domain_list = set()
    ip_domain_map = {}
    # sld_ip_map = {}
    
    # Extract domain names from DNS queries
    dns_output = os.popen(f"tshark -r {pcap_file} -Y \"dns.flags.response==1 && not mdns\" -T fields -e dns.qry.name -e dns.qry.type -e dns.a -e dns.aaaa").read()
    hosts = dns_output.splitlines()
    for line in hosts:
        line = line.split("\t")
        if len(line) < 4:
            continue
        # Local traffic filtering
        if line[0].startswith('192.168.') or line[0].startswith(ipv6_ip_block) or '.arpa' in line[0] or '.local' in line[0] or 'moniotr' in line[0] or line[0] == 'local':
            continue
        domain = line[0].lower()
        dns_type = line[1]
        ips = line[3].split(",") if dns_type == '28' else line[2].split(",")
        if domain and domain[-1] == '.':
            domain = domain[:-1]
        # sld = extract_sld(domain)
        # if not sld:
        #     continue
            
        domain_list.add(domain)
        # unique_slds.add(sld)
        for ip in ips:
            if len(ip) == 0:
                # logger.debug(f"Empty IP for domain: {domain}")
                continue
            ip_domain_map[ip] = domain
            # sld_ip_map[ip] = sld
    
    # Extract domain names from TLS handshake
    tls_output = os.popen(f"tshark -r {pcap_file} -Y \"tls.handshake.extensions_server_name\" -T fields -e tls.handshake.extensions_server_name -e ip.dst").read()
    tls_hosts = tls_output.splitlines()
    for line in tls_hosts:
        line = line.split("\t")
        if len(line) < 2:
            continue
        if line[1].startswith('192.168.') or 'in-addr.arpa' in line[1] or '.local' in line[1]:
            continue
        domain = line[0].lower()
        if domain and domain[-1] == '.':
            domain = domain[:-1]
        ip = line[1]
        
        # sld = extract_sld(domain)
        # unique_slds.add(sld)
        domain_list.add(domain)
        # for ip in ips:
        ip_domain_map[ip] = domain
            # sld_ip_map[ip] = sld
        
        
    
    return domain_list, ip_domain_map
