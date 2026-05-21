# Mini Internet Protocol Stack Simulator

A Python simulation of a simplified network stack implementing Layer 2 (Data Link), Layer 3 (Network), and Layer 4 (Transport) to deliver data between two hosts across a router.

## Group Members
- Nour Zahrawi - 24106807
- Ben Holliday - 24443977


## How to Run

```bash
python main.py <message_size>
```

**Example:**
```bash
python main.py 10    # sends a 10-byte message
python main.py 100   # sends a 100-byte message
python main.py 600   # sends a 600-byte message (triggers segmentation)
```

## File Structure

| File | Description |
|------|-------------|
| `main.py` | Entry point. Initialises devices, builds the message, and drives the end-to-end simulation |
| `protocol.py` | Header class definitions for all three layers: `segment` (L4), `packet` (L3), `frame` (L2) |
| `devices.py` | `Host` and `Router` class implementations handling all layer logic |
| `config.py` | Fixed network parameters: IP addresses, MAC addresses, routing tables, and interface definitions |
| `README.md` | This file |

## Network Topology

```
Host A ----------- Router R1 ----------- Host B
(10.0.1.10)   (10.0.1.1 / 10.0.2.1)   (10.0.2.20)
```

## Requirements

- Python 3.x
- No external libraries required
