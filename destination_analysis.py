import argparse
import concurrent.futures
from src.analysis.extract_domain import compute_unique_domains
from src.analysis.ip_to_domain import compute_ip_to_domain
from src.analysis.comparison import compare_domain_list
from src.utils import *



def main():
    parser = argparse.ArgumentParser(description="IoT Traffic Analysis Tool")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommand: Compute unique domains
    domain_parser = subparsers.add_parser("domains", help="Compute unique domains")
    domain_parser.add_argument("--input_file", required=True, help="File with path to input PCAP files")
    domain_parser.add_argument("--output_dir", required=True, help="Output dir for unique domains")
    # domain_parser.add_argument("--sld", action='store_const', default=False, const=True, help="output slds instead of full domain names")
    domain_parser.add_argument("--exp", help="Experiment name for logging")

    # Subcommand: Extract IPs from PCAP files
    ip_map_parser = subparsers.add_parser("map_ips", help="Extract IPs")
    ip_map_parser.add_argument("--input_file", help="File with path to input PCAP files")
    # ip_map_parser.add_argument("--ip_file_dir", help="Input IP files directory")
    ip_map_parser.add_argument("--output_dir", required=True, help="Output dir for IP mappings")
    # ip_map_parser.add_argument("--sld", action='store_const', default=False, const=True, help="output slds instead of full domain names")
    ip_map_parser.add_argument("--exp", help="Experiment name for logging")


    # Subcommand: Compare domain lists
    compare_parser = subparsers.add_parser("compare_domains", help="Compare SLD lists")
    compare_parser.add_argument("--file1", required=True, help="First domain list file")
    compare_parser.add_argument("--file2", required=True, help="Second domain list file")
    compare_parser.add_argument("--output_dir", required=True, help="Output dir for differences")
    compare_parser.add_argument("--exp", help="Experiment name for logging")

    args = parser.parse_args()
    if args.exp:
        exp_name = args.exp
    else:
        exp_name = "destination"
    logger = setup_logger(log_file=f"logs/{args.command}_{exp_name}_analysis.log")

    if args.command == "domains":
        compute_unique_domains(args.input_file, args.output_dir)
    elif args.command == "map_ips":
        # extract IPs from PCAP files 
        if args.input_file:
            compute_ip_to_domain(args.input_file, args.output_dir)
        # elif args.ip_file_dir:
        #     compute_ip_to_domain(args.ip_file_dir, args.output_dir, args.sld, ip_files=True)
        else:
            logger.error("Please provide either --input_file ")
    elif args.command == "compare_domains":
        compare_domain_list(args.file1, args.file2, args.output_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
