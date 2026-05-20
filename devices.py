from config import *
from protocol import frame, packet, segment

class Host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.mac_table = {} # {ip: mac}
    
    #MAC learning
    def learn_mac(self, ip, mac):
        self.mac_table[ip] = mac
        print(f"{self.name}: Layer 2: Source MAC learned: {mac}")

    #MAC lookup
    def lookup_mac(self, ip):
        return self.mac_table.get(ip, None)
    
    #Send frame
    def send_frame(self, dst_mac, packet):
        f = frame(self.mac, dst_mac, packet)
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")
        return f
    
    #Recieve frame
    def receive_frame(self, f):
        self.learn_mac(f.data.src_ip, f.src_mac)
        print(f"{self.name}: Layer 2: Frame received")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        return f.data  
    
    def receive_packet(self, pkt):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={pkt.src_ip}, DST_IP={pkt.dst_ip}, TTL={pkt.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {pkt.dst_ip}")
        print(f"{self.name}: Layer 3: Packetindentified as local delivery.")
        return pkt.data  
    
class Router:
    def __init__(self, name, interfaces, routing_table):
        self.name = name   #interfaces = {interface_id: {"ip":..., "mac":...}}
        self.interfaces = interfaces   #routing_table = {network: {"next_hop": ..., "interface": ...}}
        self.routing_table = routing_table
        self.mac_table = {} #{ip: (mac, interface_id)}

    #MAC learning (L2)
    def learn_mac(self, ip, mac, interface_id):
        self.mac_table[ip] = (mac, interface_id)
        print(f"{self.name}: Layer 2: Source MAC learned: {mac} on interface {interface_id}")

    #MAC lookup (L2)
    def lookup_mac(self, ip):
        return self.mac_table.get(ip, None)
    
    #Routing table lookup (L3)
    def route(self, dst_ip):
        for network, info in self.routing_table.items():
            network_addr, prefix = network.split('/')
            if dst_ip.rsplit(".", 1)[0] == network_addr.rsplit(".", 1)[0]: 
                return info['next_hop'], info['interface']
        return None, None 
    
    #recieve frame, pass packet to Layer 3 (L2)
    def receive_frame(self, f, interface_id):
        self.learn_mac(f.data.src_ip, f.src_mac, interface_id)
        print(f"{self.name}: Layer 2: Frame received on Interface {interface_id}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        return f.data
    
    #forward packet (L3)
    def forward_packet(self, pkt):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={pkt.src_ip}, DST_IP={pkt.dst_ip}, TTL={pkt.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {pkt.dst_ip}")

        pkt.ttl -= 1
        print(f"{self.name}: Layer 3: TTL decremented: {pkt.ttl + 1} -> {pkt.ttl}")
        if pkt.ttl == 0:
            print(f"{self.name}: Layer 3: TTL expired, packet dropped")
            return None
        
        #routing
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        next_hop, interface_id = self.route(pkt.dst_ip)
        print (f"{self.name}: Layer 3: Next hop determined: {next_hop}")
        print(f"{self.name}: Layer 3: Outgoing interface selected (Interface {interface_id})")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        #wrap in new frame
        src_mac = self.interfaces[interface_id]['mac']
        dst_mac_entry = self.lookup_mac(next_hop)
        dst_mac = dst_mac_entry[0] if dst_mac_entry else None

        f = frame(src_mac, dst_mac, pkt)
        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop}) → {dst_mac}")
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={src_mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame forwarded on Interface {interface_id}")
        return f