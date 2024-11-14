import socket
import struct
import time
import os
import sys
import threading
import argparse
import platform

# Default values for options
max_hops = 30
timeout = 2  # Default timeout in seconds
interval = 1  # Default interval between probes
flood_mode = False  # Default to not using flood mode
fast_mode = False  # Default to not using fast mode
ping_count = 4  # Number of echo requests to send
packet_size = 56  # Default packet size (in bytes)
ttl = 64  # Default TTL
resolve = False  # Resolve IP to hostname
dont_fragment = False  # Default Don't Fragment flag (IPv4-only)
record_route = False  # Default to not recording route (IPv4)
timestamp = False  # Default to not using timestamp
source_route = None  # No source route by default
source_address = None  # No source address by default
ipv6 = False  # Default to use IPv4
tos = 0  # Default TOS (Type of Service)
reverse_route = False  # Reverse route for IPv6
compartment = None  # Routing compartment (not often used)
hyperv = False  # Hyper-V address ping (optional)
verbose = False  # Verbose output

# Function to create a simple ICMP Echo Request packet
def create_packet(id, size, ttl, dont_fragment=False, tos=0, timestamp=False, source_route=None):
    """Create a basic ICMP Echo Request packet with specified options."""
    # Create ICMP Echo Request Header (Type 8, Code 0)
    header = struct.pack('bbHHh', 8, 0, 0, id, 1)  # Type, Code, Checksum, ID, Sequence
    checksum = calculate_checksum(header + b'\x00' * (size - 8))  # Fill with padding to match the requested size
    header = struct.pack('bbHHh', 8, 0, checksum, id, 1)

    return header

# Function to calculate checksum (used to verify packet integrity)
def calculate_checksum(source_string):
    """Calculate checksum for the ICMP packet."""
    checksum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0
    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        checksum = checksum + this_val
        checksum = checksum & 0xFFFF
        count = count + 2
    if count_to < len(source_string):
        checksum = checksum + source_string[len(source_string) - 1]
        checksum = checksum & 0xFFFF
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = checksum + (checksum >> 16)
    checksum = ~checksum & 0xFFFF
    return checksum

# Function to perform the PingSploit action
def pingsploit(dest_name, max_hops=30, timeout=2, interval=1, flood=False, fast=False):
    dest_ip = socket.gethostbyname(dest_name)
    print(f"PingSploit to {dest_name} ({dest_ip}), {max_hops} hops max:")

    for ttl in range(1, max_hops + 1):
        # Create a raw socket
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        icmp_socket.settimeout(timeout)

        # Create packet
        packet_id = os.getpid() & 0xFFFF
        packet = create_packet(packet_id, packet_size, ttl, dont_fragment, tos, timestamp, source_route)

        if flood:
            flood_thread = threading.Thread(target=flood_mode_function, args=(icmp_socket, dest_ip, packet, ttl, interval))
            flood_thread.start()
            flood_thread.join()
        else:
            start_time = time.time()
            try:
                icmp_socket.sendto(packet, (dest_ip, 0))
                data, addr = icmp_socket.recvfrom(1024)
                end_time = time.time()

                rtt = (end_time - start_time) * 1000  # RTT in milliseconds
                print(f"{ttl}\t{addr[0]}\t{rtt:.2f} ms")
            except socket.timeout:
                print(f"{ttl}\t*\tRequest Timed Out")
        time.sleep(interval)

        if fast and ttl == 1:
            print("Fast mode: Stopping after first hop.")
            break

        icmp_socket.close()

# Flood Mode Function
def flood_mode_function(icmp_socket, dest_ip, packet, ttl, interval):
    """Send a flood of packets in flood mode."""
    while True:
        icmp_socket.sendto(packet, (dest_ip, 0))
        time.sleep(interval)

# Function to parse command-line arguments
def parse_args():
    """Parse command-line arguments."""
    global max_hops, timeout, interval, flood_mode, fast_mode, ping_count, packet_size, ttl, resolve, dont_fragment
    global record_route, timestamp, source_route, source_address, ipv6, tos, reverse_route, compartment, hyperv, verbose

    parser = argparse.ArgumentParser(description="PingSploit: Advanced ping and traceroute tool.")

    # Add arguments for various ping options
    parser.add_argument("destination", help="The destination host to ping or traceroute to")
    parser.add_argument("-t", "--ping-forever", action="store_true", help="Ping the specified host until stopped (Ctrl+C to stop).")
    parser.add_argument("-n", "--count", type=int, default=ping_count, help="Number of echo requests to send.")
    parser.add_argument("-l", "--size", type=int, default=packet_size, help="Size of each ping packet.")
    parser.add_argument("-f", "--dont-fragment", action="store_true", help="Set the Don't Fragment flag in packet (IPv4 only).")
    parser.add_argument("-i", "--ttl", type=int, default=ttl, help="Set Time To Live (TTL).")
    parser.add_argument("-v", "--tos", type=int, default=tos, help="Set Type of Service (TOS, IPv4 only).")
    parser.add_argument("-r", "--record-route", type=int, help="Record route for given hops (IPv4 only).")
    parser.add_argument("-s", "--timestamp", type=int, help="Timestamp for given hops (IPv4 only).")
    parser.add_argument("-j", "--loose-source-route", type=str, help="Loose source route along host list (IPv4 only).")
    parser.add_argument("-k", "--strict-source-route", type=str, help="Strict source route along host list (IPv4 only).")
    parser.add_argument("-w", "--timeout", type=int, default=timeout, help="Timeout in milliseconds.")
    parser.add_argument("-R", "--reverse-route", action="store_true", help="Test reverse route (IPv6 only).")
    parser.add_argument("-S", "--source-address", type=str, help="Source address to use.")
    parser.add_argument("-4", "--ipv4", action="store_true", help="Force IPv4.")
    parser.add_argument("-6", "--ipv6", action="store_true", help="Force IPv6.")
    parser.add_argument("--flood", action="store_true", help="Flood the server with packets.")
    parser.add_argument("-a", "--resolve", action="store_true", help="Resolve IP addresses to hostnames.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    
    args = parser.parse_args()

    # Update global settings with parsed arguments
    return args

# Main execution flow
if __name__ == "__main__":
    args = parse_args()
    pingsploit(args.destination, args.count, args.timeout, args.size, args.flood, args.ping_forever)
