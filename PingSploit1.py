import os
import time
import socket
import subprocess
import random
import string
import argparse
import sys
from scapy.all import ICMP, IP, send
import curses

# Banners for PingSploit
banners = [
    """
    ____              _   _     ____    ____     ____      _       U  ___ u           _____   
    U|  _"\ u  ___     | \ |"| U /"___|u / __"| uU|  _"\ u  |"|       \/"_ \/  ___     |_ " _|  
    \| |_) |/ |_"_|   <|  \| |>\| |  _ /<\___ \/ \| |_) |/U | | u     | | | | |_"_|      | |    
     |  __/    | |    U| |\  |u | |_| |  u___) |  |  __/   \| |/__.-,_| |_| |  | |      /| |\   
     |_|     U/| |\u   |_| \_|   \____|  |____/>> |_|       |_____|\_)-\___/ U/| |\u   u |_|U   
     ||>>_.-,_|___|_,-.||   \\,-._)(|_    )(  (__)||>>_     //  \\      \\.-,_|___|_,-._// \\_  
    (__)__)\_)-' '-(_/ (_")  (_/(__)__)  (__)    (__)__)   (_")("_)    (__)\_)-' '-(_/(__) (__)  but sometimes it can also be                                                                                         
    .-'''-.                   .---.   '   _    \                
    _________   _...._      .--.   _..._                      _________   _...._      |   | /   /` '.   \ .--.          
    \        |.'      '-.   |__| .'     '.   .--./)           \        |.'      '-.   |   |.   |     \  ' |__|          
     \        .'```'.    '. .--..   .-.   . /.''\\             \        .'```'.    '. |   ||   '      |  '.--.     .|   
      \      |       \     \|  ||  '   '  || |  | |             \      |       \     \|   |\    \     / / |  |   .' |_  
       |     |        |    ||  ||  |   |  | \`-' /          _    |     |        |    ||   | `.   ` ..' /  |  | .'     | 
       |      \      /    . |  ||  |   |  | /("'`         .' |   |      \      /    . |   |    '-...-'`   |  |'--.  .-' 
       |     |\`'-.-'   .'  |  ||  |   |  | \ '---.      .   | / |     |\`'-.-'   .'  |   |               |  |   |  |   
       |     | '-....-'`    |__||  |   |  |  /'""'.\   .'.'| |// |     | '-....-'`    |   |               |__|   |  |   
      .'     '.                 |  |   |  | ||     ||.'.'.-'  / .'     '.             '---'                      |  '.' 
    '-----------'               |  |   |  | \'. __// .'   \_.''-----------'                                      |   /  
                                '--'   '--'  `'---'                                                              `'-'   
    """,
    """
                                     .-+#%%%@@@@@@@@@%%%#*-.                                        
                                   .*@@@@@@@@@@@@@@@@@@@@@@@#:.                                     
                                  .%@@@@@@@@@@@@@@@@@@@@@@@@@@*.                                    
                                 .+@@@@@@@@@@@@@@@@@@@@@@@@@@@@+                                    
                                  *@@@@@@@@@@@@@@@@@@@@@@@@@@@@#                                    
                                  *@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                                    
                                  *@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                                    
                                  %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+***+=:.                            
                         ...::--::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%-.                          
                       .:=%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=.                          
                       -@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+                            
                       .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%:.                            
                       ..=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*-.                              
                          .=#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*..                                 
                            ..+#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+                                  
                               .:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..                                 
                                .*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%..                                 
                                 :@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:.                                  
                                  :@@@@@@@@@@@@@@@@@@@@@@@@@@@@#.                                   
                                   -*%@@@@@@@@@@@@@@@@@@@@@@@@@:.                                   
                                     *@@@@@@@@@@@@@@@@@@@@@@@#:.                                    
                                     +@@@@@@@@@@@@@@@@@@@@@@#.                                      
                                    .#@@@@@@@@@@@@@@@@@@@@@@*.                                      
                                 ..=@@@@@@@@@@@@@@@@@@@@@@@@@+.                                     
                               ...*@@@@@@@@@@@@@@@@@@@@@@@@@@@=.....                                
                               ..*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@......                               
                              ..%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*.....                               
                              .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#-.                                
                            -*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*-.                            
                         :*%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#*:.                        
                     .:=#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+-..                     
                ...:=%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*-:. .                
                .*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#=..              
             -*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*..          
           .#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%=.         
          .*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*.        
          =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*.       
         :@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*.      
        .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=.     
        =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%.     
       .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+.    
       -@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..   
      .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+    
      :@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%.   
      =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:   
      =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+.  
     .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%.  
     .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*. 
     =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@: 
    .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+ 
    :@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@# 
   :#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.
    """
]

# Function to print a banner based on the index
def print_banner(stdscr, banner_index):
    stdscr.clear()
    stdscr.addstr(0, 0, banners[banner_index])
    stdscr.refresh()
    time.sleep(2)  # Show the banner for 2 seconds

# Helper function to display help message
def print_help():
    help_message = """
    Usage: Pingsploit [options] [target]

    Options:
    -t             Ping the specified host until stopped.
    -a             Resolve addresses to hostnames.
    -n count       Number of echo requests to send.
    -l size        Send buffer size.
    -f             Set Don't Fragment flag in packet (IPv4-only).
    -i TTL         Time To Live.
    -v TOS         Type Of Service (IPv4-only).
    -r count       Record route for count hops (IPv4-only).
    -s count       Timestamp for count hops (IPv4-only).
    -j host-list   Loose source route along host-list (IPv4-only).
    -k host-list   Strict source route along host-list (IPv4-only).
    -w timeout     Timeout in milliseconds to wait for each reply.
    -R             Use routing header to test reverse route (IPv6-only).
    -S srcaddr     Source address to use.
    -c compartment Routing compartment identifier.
    -p             Ping a Hyper-V Network Virtualization provider address.
    -4             Force using IPv4.
    -6             Force using IPv6.
    --flood        Flood the target with pings.
    --spoof        Spoof a ping with a custom source address.
    --help         Display this help message.
    """
    print(help_message)

# Function to perform a normal ping with the given flags
def perform_ping(destination, count, timeout, size, verbose, flags):
    cmd = f"ping -c {count} -W {timeout} -s {size} "
    
    if flags.get('a'):
        cmd += "-a "
    if flags.get('f'):
        cmd += "-f "
    if flags.get('i'):
        cmd += f"-i {flags['i']} "
    if flags.get('v'):
        cmd += f"-v {flags['v']} "
    if flags.get('r'):
        cmd += f"-r {flags['r']} "
    if flags.get('s'):
        cmd += f"-s {flags['s']} "
    if flags.get('j'):
        cmd += f"-j {flags['j']} "
    if flags.get('k'):
        cmd += f"-k {flags['k']} "
    if flags.get('w'):
        cmd += f"-w {flags['w']} "
    if flags.get('R'):
        cmd += "-R "
    if flags.get('S'):
        cmd += f"-S {flags['S']} "
    if flags.get('c'):
        cmd += f"-c {flags['c']} "
    if flags.get('p'):
        cmd += "-p "
    if flags.get('4'):
        cmd += "-4 "
    if flags.get('6'):
        cmd += "-6 "
    
    cmd += destination
    response = os.popen(cmd).read()
    print(response)
    if verbose:
        print(response)

# Function to perform spoofed ping using raw sockets
def spoofed_ping(target_ip, source_ip, count):
    print(f"Performing spoofed ping to {target_ip} with source {source_ip}")
    for _ in range(count):
        packet = IP(src=source_ip, dst=target_ip) / ICMP()
        send(packet, verbose=False)
        time.sleep(1)

# Function for flooding pings
def flood_ping(target_ip, count):
    print(f"Flooding {target_ip} with pings...")
    while True:
        cmd = f"ping -f -c {count} {target_ip}"
        os.system(cmd)

# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="PingSploit - A Pinging Tool")
    parser.add_argument("target", help="Target IP or domain", nargs="?")
    parser.add_argument("-t", action="store_true", help="Ping the target until stopped")
    parser.add_argument("-a", action="store_true", help="Resolve addresses to hostnames")
    parser.add_argument("-n", type=int, default=4, help="Number of echo requests to send")
    parser.add_argument("-l", type=int, default=56, help="Send buffer size")
    parser.add_argument("-f", action="store_true", help="Set Don't Fragment flag in packet (IPv4-only)")
    parser.add_argument("-i", type=int, help="Time To Live")
    parser.add_argument("-v", type=int, help="Type Of Service")
    parser.add_argument("-r", type=int, help="Record route for count hops (IPv4-only)")
    parser.add_argument("-s", type=int, help="Timestamp for count hops (IPv4-only)")
    parser.add_argument("-j", type=str, help="Loose source route along host-list (IPv4-only)")
    parser.add_argument("-k", type=str, help="Strict source route along host-list (IPv4-only)")
    parser.add_argument("-w", type=int, help="Timeout in milliseconds")
    parser.add_argument("-R", action="store_true", help="Use routing header for reverse route (IPv6-only)")
    parser.add_argument("-S", type=str, help="Source address to use")
    parser.add_argument("-c", type=int, help="Routing compartment identifier")
    parser.add_argument("-p", action="store_true", help="Ping a Hyper-V Network Virtualization provider address")
    parser.add_argument("-4", action="store_true", help="Force using IPv4")
    parser.add_argument("-6", action="store_true", help="Force using IPv6")
    parser.add_argument("--flood", action="store_true", help="Flood the target with pings")
    parser.add_argument("--spoof", action="store_true", help="Spoof a ping with a custom source address")
    parser.add_argument("--help", action="store_true", help="Display this help message")

    return parser.parse_args()

def main():
    args = parse_args()

    if args.help:
        print_help()
        return

    # Display a random banner
    stdscr = curses.initscr()
    banner_index = random.randint(0, len(banners) - 1)
    print_banner(stdscr, banner_index)

    # Ensure target is specified
    if not args.target:
        print("No target specified. Use --help for usage instructions.")
        return

    flags = vars(args)

    if args.flood:
        flood_ping(args.target, args.n)
    elif args.spoof:
        source_ip = input("Enter the source IP to spoof: ")
        spoofed_ping(args.target, source_ip, args.n)
    else:
        perform_ping(args.target, args.n, args.w, args.l, False, flags)

if __name__ == "__main__":
    main()
