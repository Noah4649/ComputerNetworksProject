from config import *
from protocol import frame, packet, segment

class Host:
    def __init__(self, name, ip, mac, default_gateway_ip):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.mac_table = {} # {ip: mac}
        self.default_gateway_ip = default_gateway_ip
        self.next_seq = 0
    
    #Creates a new segment with alternating sequence number
    def create_data_segment(self, src_port, dst_port, data):
        seg = segment(src_port, dst_port, data, "DATA", self.next_seq)
        self.next_seq = 1 - self.next_seq
        return seg

    #MAC learning
    def learn_mac(self, ip, mac):
        self.mac_table[ip] = mac
        print(f"{self.name}: Layer 2: Source MAC learned: {mac}")

    #MAC lookup
    def lookup_mac(self, ip):
        return self.mac_table.get(ip, None)
    
    #Calculate next IP hop for destination
    def next_hop(self, dst_ip):
        if dst_ip.rsplit(".", 1)[0] == self.ip.rsplit(".", 1)[0]:
            return dst_ip
        else:
            return self.default_gateway_ip
    
    #Send frame
    def send_frame(self, dst_mac, packet):
        f = frame(self.mac, dst_mac, packet)
        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame sent")
        return f
    
    #receive frame
    def receive_frame(self, f):
        self.learn_mac(f.packet.src_ip, f.src_mac)
        print(f"{self.name}: Layer 2: Frame received")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        return f.packet
    
    #Send data to next hop
    def send_data(self, dst_ip, data, src_port=5000, dst_port=80): #hardcoded src and dst ports. Needs to be changed
        print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(data)}") #length needs to change from this formula to property
        
        seg = self.create_data_segment(src_port, dst_port, data)
        print(f"{self.name}: Layer 4: Checksum computed")
        print(f"{self.name}: Layer 4: Segment created by adding transport layer header ({seg.type}, seq={seg.seq_number})")
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")
        
        pkt = packet(self.ip, dst_ip, seg)
        print(f"{self.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.ip}, DST_IP={dst_ip}, TTL={pkt.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")
        
        next_hop_ip = self.next_hop(dst_ip)
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected")        
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
        
        next_hop_mac = self.lookup_mac(next_hop_ip)
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {next_hop_mac}")
        return self.send_frame(next_hop_mac, pkt)

    def create_ack_segment(self, received_segment):
        ack_seg = segment(received_segment.dst_port, received_segment.src_port, "", "ACK", received_segment.seq_number)
        print(f"{self.name}: Layer 4: Segment created by adding Transport Layer header (ACK, seq={ack_seg.seq_number})")
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")
        return ack_seg
    
    def receive_packet(self, pkt):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={pkt.src_ip}, DST_IP={pkt.dst_ip}, TTL={pkt.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {pkt.dst_ip}")
        print(f"{self.name}: Layer 3: Packet identified as local delivery")
        print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")

        seg = pkt.segment

        print(f"{self.name}: Layer 4: Segment received from Network Layer")

        if not seg.verify_checksum():
            print(f"{self.name}: Layer 4: Segment discarded due to checksum error")
        else: 
            print(f"{self.name}: Layer 4: Checksum verified")

            if seg.type == "DATA":
                print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(seg.data)}")
                return self.send_ack(pkt)
            
            elif seg.type == "ACK":
                print(f"{self.name}: Layer 4: ACK received: seq={seg.seq_number}")
        
        return None

    def send_ack(self, received_packet):
        ack_seg = self.create_ack_segment(received_packet.segment)
        ack_pkt = packet(self.ip, received_packet.src_ip, ack_seg)
        print(f"{self.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.ip}, DST_IP={received_packet.src_ip}")
        print(f"{self.name}: Layer 3: Destination IP read: {received_packet.src_ip}")

        next_hop_ip = self.next_hop(received_packet.src_ip)
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")

        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
        next_hop_mac = self.lookup_mac(next_hop_ip)
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {next_hop_mac}")
        ack_frm = self.send_frame(next_hop_mac, ack_pkt)
        return ack_frm
    
class Router:
    def __init__(self, name, interfaces, routing_table):
        self.name = name   #interfaces = {interface_id: {"ip":..., "mac":...}}
        self.interfaces = interfaces   #routing_table = {network: {"next_hop": ..., "interface": ...}}
        self.routing_table = routing_table
        self.mac_table = {} #{ip: (mac, interface_id)}

    #MAC learning (L2)
    def learn_mac(self, ip, mac, interface_id):
        self.mac_table[ip] = (mac, interface_id)
        print(f"{self.name}: Layer 2: Source MAC learned: {mac} on Interface {interface_id}")

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
    
    #receive frame, pass packet to Layer 3 (L2)
    def receive_frame(self, f, interface_id):
        self.learn_mac(f.packet.src_ip, f.src_mac, interface_id)
        print(f"{self.name}: Layer 2: Frame received on Interface {interface_id}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        return f.packet
    
    #forward packet (L3)
    def forward_packet(self, pkt):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={pkt.src_ip}, DST_IP={pkt.dst_ip}, TTL={pkt.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {pkt.dst_ip}")

        pkt.ttl -= 1
        print(f"{self.name}: Layer 3: TTL decremented: {pkt.ttl + 1} → {pkt.ttl}")
        if pkt.ttl == 0:
            print(f"{self.name}: Layer 3: TTL expired, packet dropped")
            return None
        
        #routing
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        next_hop, interface_id = self.route(pkt.dst_ip)
        print (f"{self.name}: Layer 3: Next-hop determined: {next_hop}")
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
    
    #forward packet
    def process_frame(self, frame, interface_id):
        packet = self.receive_frame(frame, interface_id)
        return self.forward_packet(packet)