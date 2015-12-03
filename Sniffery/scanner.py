import threading
import time
import netaddr import IPNetwork, IPAddress

host = "192.168.1.4"

subnet = "192.168.0.0/24"

magic_messege = "WUSZ RZECZNY JEST NIEBEZPIECZNY!!!!"

def udp_sender(subnet, magic_messege):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_messege,("%s" % ip, 65212))
        except:
            pass

try:
    while True:
        if icmp_header.code == 3 and icmp_header.type == 3:
            if IPAddress(icmp_header.src_address) in IPNetwork(subnet):
                if raw_bufffer[len(raw_bufffer)-len(magic_messege):] == magic_messege:
                    print "Host: %s" % icmp_header.src_address
