# Segment is transport layer of OSI stack - innermost wrapper
class segment:
    def __init__(self, src_port, dst_port, data):
        self.src_port = src_port
        self.dst_port = dst_port
        self.data = data
        self.length = len(data) + 10
        # compute the checksum
        # self.checksum 
        # type needs to be ack or data
        # self.type
        # seq number alternates between 0 and 1
        # self.seq_number


# Packet is network layer of OSI stack - middle wrapper
# class packet:


# Frame is data link layer of OSI stack - outermost wrapper
class frame:
    def __init__(self, src_mac, dst_mac, data):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.data = data
        self.type = 0x0800
        self.length = 14 + (data.length if hasattr(data, 'length') else len(data))