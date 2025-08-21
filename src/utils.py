import logging
import os
import sys
import json
import subprocess
import tldextract
from collections import defaultdict
import csv
import multiprocessing
import concurrent
import pickle
import ipaddress

ipv6_ip_block = '2001:470:8863:1aba'
dataset_root_path = '/net/data/iot-longitudinal/datasets' # cfg['dataset_root_path']

def output_file_generator(out_dir:str, basename:str, device:str, file:str) -> str:
    tmp_dir = os.path.join(out_dir, basename)
    if not os.path.exists(tmp_dir):
        os.system('mkdir -pv %s' % tmp_dir)
    output_file = os.path.join(tmp_dir, device + file) # Output file
    return output_file

def setup_logger(log_file="analysis.log", level=logging.DEBUG):
    # Create or get the root logger
    logger = logging.getLogger()
    
    # Set the logging level
    logger.setLevel(level)
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file, mode='a+')
    file_handler.setLevel(level)
    
    # Create a stream handler (for console output)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    
    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set the formatter for both handlers
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # Avoid adding duplicate handlers if this function is called multiple times
    if not logger.hasHandlers():
        # Add the file and stream handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    
    # Log the initial message
    logger.info("---------------------------------------------")
    logger.info("---|| IoT Longitudinal Project Destination Analysis ||---")
    logger.info("---------------------------------------------")
    return logger

def ensure_dir_exists(directory):
    """Ensure a directory exists, create if not."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def get_device_name(full_path, dataset_root_path):
    """
    Extract the device name from the given path, which can have two structures:
    1. dataset_root_path/dataset_year/dataset/device-name/exp-name/pcaps
    2. dataset_root_path/dataset_year/dataset/device-name/pcaps

    Args:
        full_path (str): The full path of the current directory or file.
        dataset_root_path (str): The root path of the dataset.

    Returns:
        str: The name of the device.
    """
    # Normalize the paths to ensure consistent behavior across OS
    dataset_root_path = os.path.normpath(dataset_root_path)
    new_full_path = os.path.normpath(full_path)

    # Calculate the relative path from the dataset root to the full path
    relative_path = os.path.relpath(new_full_path, dataset_root_path)

    # Split the relative path into its components
    path_parts = relative_path.split(os.sep)

    # Ensure the path structure is valid and extract the device name
    if len(path_parts) >= 3 and path_parts[2]:
        return path_parts[2]  # 'device-name' (Case 1 or 2)

    raise ValueError(f"Unexpected path structure: {new_full_path}")



# def is_local(ip_src, ip_dst):
#     LOCAL_IPS = ['129.10.227.248', '129.10.227.207']
#     is_local = False
#     try:
#         is_local = (ipaddress.ip_address(ip_src).is_private and ipaddress.ip_address(ip_dst).is_private
#                 ) or (ipaddress.ip_address(ip_src).is_private and (ip_dst in LOCAL_IPS) 
#                 ) or (ipaddress.ip_address(ip_dst).is_private and (ip_src in LOCAL_IPS)) # =="129.10.227.248" or ip_dst=="129.10.227.207"
#     except:
#         # print('Error:', ip_src, ip_dst)
#         return 1
#     return is_local

def is_local_address(ip_str):
    LOCAL_IPS = ['129.10.227.248', '129.10.227.207']
    try:
        if ip_str == "::" or ip_str == "::1":
            return True
        if is_ipv6(ip_str):
            ip = ipaddress.IPv6Address(ip_str)
            return ip.is_multicast or ip.is_link_local or (
                ip.is_private and check_in_network("fc00::/7", ip)
                ) or ip.is_unspecified
        else:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private or ip.is_multicast or ip == ipaddress.IPv4Address("255.255.255.255") or ip_str in LOCAL_IPS
    except:
        return False

def check_in_network(network_prefix, ip):
    if ip is None or network_prefix is None:
        return False
    network = ipaddress.IPv6Network(network_prefix, strict=False)
    return ip in network

def is_ipv6(address:str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
        if isinstance(ip, ipaddress.IPv6Address):
            # print("{} is an IPv6 address".format(address))
            return True
        else:
            return False
    except ValueError:
        return False
    
def is_valid_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False
