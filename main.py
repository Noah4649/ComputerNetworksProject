import sys
from config import *
from protocol import frame, packet, segment
from devices import Host, Router 

#create hosts
host_a = Host(HOST_A_NAME, HOST_A_IP, HOST_A_MAC_ADDRESS, ROUTER1_INTERFACE1_IP)
host_b = Host(HOST_B_NAME, HOST_B_IP, HOST_B_MAC_ADDRESS, ROUTER1_INTERFACE2_IP)

#create router
router_a = Router("Router_A", ROUTER1_INTERFACES, ROUTING_TABLE) 

# create static MAC tables
host_a.mac_table[ROUTER1_INTERFACE1_IP] = ROUTER1_INTERFACE1_MAC_ADDRESS
host_b.mac_table[ROUTER1_INTERFACE2_IP] = ROUTER1_INTERFACE2_MAC_ADDRESS
router_a.mac_table[HOST_A_IP] = (HOST_A_MAC_ADDRESS, 1)
router_a.mac_table[HOST_B_IP] = (HOST_B_MAC_ADDRESS, 2)


def send_one_segment(data):
    correct_ack = False
    while not correct_ack:
        #send data from host a
        frm = host_a.send_data(HOST_B_IP, data)

        # Router receives frame on interface 1 and forwards it to the correct network
        forwarded_frm = router_a.process_frame(frm, 1)

        # Host B receives packet and sends ack
        host_b_pkt = host_b.receive_frame(forwarded_frm)
        ack_frm = host_b.receive_packet(host_b_pkt)

        # Router receives ACK from Host B on interface 2 and forwards it to the correct network
        if ack_frm is None:
            print("No ACK received")
            continue
        forwarded_ack_frm = router_a.process_frame(ack_frm, 2)

        # Host A receives the ACK
        host_a_ack_pkt = host_a.receive_frame(forwarded_ack_frm)
        host_a.receive_packet(host_a_ack_pkt)
    
        #was correct ack sequence number received
        if host_a_ack_pkt.segment.seq_number == frm.packet.segment.seq_number:
            correct_ack = True
        else:
            print(f"Host A: Layer 4: Incorrect ACK received. Retransmitting segment seq={frm.packet.segment.seq_number}")


#create message payload
message_size = int(sys.argv[1])
app_data = "X" * message_size


#main loop - break up the data into chunks of maximum 500 and send
data_parts=[]
for i in range(0,len(app_data), 500):
    data_parts.append(app_data[i:i +500])
            
#send data parts individually
for data in data_parts:
    send_one_segment(data)