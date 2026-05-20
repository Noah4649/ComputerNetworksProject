# Segment is transport layer of OSI stack - innermost wrapper
class segment:
    def __init__(self, src_port, dst_port, data, dtype, seq_number):
        self.src_port = src_port
        self.dst_port = dst_port
        self.data = data
        self.data_length = len(data)
        self.length = self.data_length + 10
        self.type = dtype #could be converted to boolean. Either ACK or DATA
        self.seq_number = seq_number #could be converted to boolean. seq_number alternates between 0 and 1
        self.checksum = self.calc_checksum()

    def calc_checksum(self):
        return sum(ord(char) for char in self.data) % 65535
    
    def verify_checksum(self):
        if self.checksum == self.calc_checksum():
            return True
        else:
            return False

# Packet is network layer of OSI stack - middle wrapper
class packet:
    def __init__(self, src_ip, dst_ip, segment, ttl=100, protocol=17):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.segment = segment
        self.length = 12 + segment.length
        self.ttl = ttl
        self.protocol = protocol

# Frame is data link layer of OSI stack - outermost wrapper
class frame:
    def __init__(self, src_mac, dst_mac, packet):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.packet = packet
        self.type = 0x0800  #IPv4 ethertype
        self.length = 14 + packet.length