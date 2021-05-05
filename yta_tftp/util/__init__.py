"""YTA TFTP Server Utility methods and datastructures"""
import socket
import struct
from dataclasses import dataclass
from enum import Enum


class TFTPOpcodes(Enum):
    """TFTP Opcodes Enum"""

    RRQ = 1  # Read request.	RFC 1350, RFC 2090
    WRQ = 2  # Write request.	RFC 1350
    DATA = 3  # Read or write the next block of data.	RFC 1350
    ACK = 4  # Acknowledgment.	RFC 1350
    ERROR = 5  # Error message.	RFC 1350
    OACK = 6  # Option acknowledgment.	RFC 2347


@dataclass()
class TFTPPacketRRQ:
    """Packet Payload Field Struct"""

    opcode: bytes
    filename: str
    mode: str


@dataclass()
class TFTPPacketDATA:
    """Packet Payload Field Struct"""

    opcode: bytes
    block_no: bytes
    data: bytes


@dataclass()
class TFTPPacketACK:
    """Packet Payload Field Struct"""

    opcode: bytes
    block_no: bytes


def unpack_tftp_rrq_packet(raw_packet: bytes) -> TFTPPacketRRQ:
    """Given bytes, will unpack to dataclass for an TFTP RRQ packet

    Q: Why don't we use struct.unpack?

    A: There is a variable length field which unpack cant handle

    Args:
        raw_packet: Bytearray received probably from a UDP socket

    Returns:
        TFTPPacketRRQ dataclass object
    """
    name_end = raw_packet.find(b"\0", 2)
    mode_end = raw_packet.find(b"\0", name_end + 1)

    return TFTPPacketRRQ(
        opcode=bytes(raw_packet[1:2]),  # byte [0] is a pad, 0x00 - skip it to stay little-endian
        filename=raw_packet[2:name_end].decode("ASCII"),
        mode=raw_packet[name_end + 1 : mode_end].decode("ASCII"),
    )


def pack_tftp_data_packet(block_no: int, data: bytes) -> bytes:
    """Given block_no and bytes (chunk) read from a file, packs to a TFTP DATA packet (bytes)
    and returns

    Args:
        block_no: TFTP DATA packets are chunks of a file. block_no is the order index.
        data: Chunk of data read from a file, probably with with 'rb' flags

    Returns:
        Bytes, a raw TFTP DATA packet
    """
    return dump_packet(
        TFTPPacketDATA(opcode=bytes([0x00, 0x03]), block_no=struct.pack("!H", block_no), data=data)
    )


def unpack_tftp_ack_packet(raw_packet: bytes) -> TFTPPacketACK:
    """Given bytes, will unpack to dataclass for an TFTP ACK packet

    Args:
        raw_packet: Bytearray received probably from a UDP socket

    Returns:
        TFTPPacketACK dataclass object
    """
    return TFTPPacketACK(*struct.unpack("!HH", raw_packet))


def dump_packet(packet_obj: object) -> bytes:
    """Given a dataclass object, will return it as a bytearray

    Args:
        packet_obj: A dataclass object

    Returns: Bytearray representing given dataclass object
    """
    raw_packet = bytearray()
    for _, value in packet_obj.__dict__.items():
        raw_packet += value

    return raw_packet


def get_socket(bind_port: int, bind_ip: str = "") -> socket:
    """Creates and returns a python socket object for UDP traffic

    Args:
        bind_port: Port to bind to and listen on
        bind_ip: IP to bind to and listen on

    Returns:
        A socket object
    """
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    _socket.bind((bind_ip, bind_port))

    return _socket
