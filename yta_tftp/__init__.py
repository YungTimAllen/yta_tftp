"""YTA TFTP Server Package"""
from os.path import isfile
import threading
import yta_tftp.util as util


class TFTPServer:
    """A TFTP Server"""

    max_bytes = 1024
    server_port = 69
    chunk_sz = 512
    listening_ip = ""

    def __init__(self, **kwargs):
        """Constructor"""
        self.source_port = self.gen_ephemeral_port()
        self.__dict__.update(kwargs)  # Probably not a good idea but its neat

    @staticmethod
    def gen_ephemeral_port():
        """Return an ephemeral port generator"""
        ephemeral_port_range = 49152, 65535
        i = ephemeral_port_range[0]
        while i < ephemeral_port_range[1]:
            yield i
            i += 1

    def run(self):
        """Main loop logic. Blocks."""
        # Server listening socket, binds to port 69 (typically)
        socket_server = util.get_socket(bind_port=self.server_port, bind_ip=self.listening_ip)

        while True:
            # Block to Rx TFTP RRQ
            raw_packet, (source_ip, source_port) = socket_server.recvfrom(self.max_bytes)  # BLOCKS

            try:
                # Unpack bytes to Datastruct
                packet_obj = util.unpack_tftp_rrq_packet(raw_packet)
                packet_obj_opcode = int.from_bytes(packet_obj.opcode, "little")

                print("Received OpCode:", util.TFTPOpcodes(value=packet_obj_opcode).name)

                # If this is a TFTP RRQ (Read Request) ...
                if packet_obj_opcode == util.TFTPOpcodes.RRQ.value:

                    # Check that the requested file exists ...
                    if isfile(packet_obj.filename):
                        # Load file to bytes and start sending DATA PDUs
                        self.reply_with_data(packet_obj, source_ip, source_port)
                    else:
                        print("! File not found. Replying with ERR PDU.")
                        self.reply_with_error(source_ip, source_port, 1)  # File not found

                # We only care about RRQ
                else:
                    print("! Received a valid TFTP packet, but it is not a RRQ. Discarding.")
                    self.reply_with_error(source_ip, source_port, 5)  # Unkown transfer ID

            # Calling enum TFTP_Opcode with an undefined value throws ValueError
            except ValueError:
                print("! Received packet that was not a TFTP RRQ packet. Discarding. (Bad OpCode)")
                self.reply_with_error(source_ip, source_port, 4)  # Illegal op

    def reply_with_error(self, dst_ip: str, dst_port: int, error_code: int):
        """Threads method handle_err_to_client

        Args:
            dst_ip: IP to address TFTP ERR PDU towards (RRQ source / calling client's IP)
            dst_port: Port to address TFTP ERR PDU towards (RRQ source / calling client's Port)
            error_code: Well-known TFTP error code to send in ERR PDU
        """
        threading.Thread(
            target=self.handle_err_to_client,
            args=(dst_ip, dst_port, error_code),
        ).start()

    def handle_err_to_client(self, dst_ip: str, dst_port: int, error_code: int):
        """Handles sending a TFTP ERR PDU to the given IP and Port

        The Error Message field of the ERR PDU is populated using Cisco defined error strings

        Args:
            dst_ip: IP to address TFTP ERR PDU towards (RRQ source / calling client's IP)
            dst_port: Port to address TFTP ERR PDU towards (RRQ source / calling client's Port)
            error_code: Well-known TFTP error code to send in ERR PDU
        """
        socket_reply = util.get_socket(bind_port=next(self.source_port), bind_ip=self.listening_ip)
        raw_tftp_error_packet = util.pack_tftp_error_packet(error_code)
        socket_reply.sendto(raw_tftp_error_packet, (dst_ip, dst_port))

    def reply_with_data(self, rrq_packet: util.TFTPPacketRRQ, dst_ip: str, dst_port: int):
        """Threads method handle_rrq_reply

        Args:
            rrq_packet: TFTPPacketRRQ datastruct, received from the listening server socket (69)
            dst_ip: IP to address TFTP DATA PDUs towards (RRQ source / calling client's IP)
            dst_port: Port to address TFTP DATA PDUs towards (RRQ source / calling client's Port)
        """
        threading.Thread(target=self.handle_rrq_reply, args=(rrq_packet, dst_ip, dst_port)).start()

    def handle_rrq_reply(self, rrq_packet: util.TFTPPacketRRQ, dst_ip: str, dst_port: int):
        """Handles a RRQ (Read Request), loading the target file, and sending TFTP DATA packets

        Args:
            rrq_packet: TFTPPacketRRQ datastruct, received from the listening server socket (69)
            dst_ip: IP to address TFTP DATA PDUs towards (RRQ source / calling client's IP)
            dst_port: Port to address TFTP DATA PDUs towards (RRQ source / calling client's Port)
        """
        reply_port = next(self.source_port)  # Its a generator
        socket_reply = util.get_socket(bind_port=reply_port, bind_ip=self.listening_ip)

        print(f"Serve {dst_ip}:{dst_port}:{rrq_packet.filename} -> {reply_port}")

        # Load file (by filename given in rrq_packet) to memory (bytes)
        with open(rrq_packet.filename, "rb") as file:
            # Take a chunk and init block number (chunk index) to 1
            chunk = file.read(self.chunk_sz)
            block_no = 1

            # While there is stuff left to read in the buffer (chunk isn't None) ...
            while chunk:

                # Pack TFTP DATA packet
                raw_tftp_data_packet = util.pack_tftp_data_packet(block_no, chunk)

                # Tx
                socket_reply.sendto(raw_tftp_data_packet, (dst_ip, dst_port))

                # Block to Rx TFTP ACK. This is a thread so it's cool.
                socket_reply.recvfrom(self.max_bytes)

                # Regular print to report progress in client's download
                if block_no == 0:
                    print(f"   Tx {rrq_packet.filename} {file.tell()/1048576}mb\t-> {reply_port}")

                # Read next chunk and increment block number
                # Block no is a uint16 value and must rollover to 0
                chunk = file.read(self.chunk_sz)
                block_no = (block_no + 1) % 65536

        print(f"Done! {dst_ip}:{dst_port}:{rrq_packet.filename} -> {reply_port}")
