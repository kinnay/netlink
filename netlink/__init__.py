
import contextlib
import itertools
import struct
import socket
import trio
import math
import os

import logging
logger = logging.getLogger(__name__)


NETLINK_ROUTE = 0
NETLINK_UNUSED = 1
NETLINK_USERSOCK = 2
NETLINK_FIREWALL = 3
NETLINK_SOCK_DIAG = 4
NETLINK_NFLOG = 5
NETLINK_XFRM = 6
NETLINK_SELINUX = 7
NETLINK_ISCSI = 8
NETLINK_AUDIT = 9
NETLINK_FIB_LOOKUP = 10
NETLINK_CONNECTOR = 11
NETLINK_NETFILTER = 12
NETLINK_IP6_FW = 13
NETLINK_DNRTMSG = 14
NETLINK_KOBJECT_UEVENT = 15
NETLINK_GENERIC = 16
NETLINK_SCSITRANSPORT = 18
NETLINK_ECRYPTFS = 19
NETLINK_RDMMA = 20
NETLINK_CRYPTO = 21
NETLINK_SMC = 22

NETLINK_INET_DIAG = NETLINK_SOCK_DIAG

NLM_F_REQUEST = 1
NLM_F_MULTI = 2
NLM_F_ACK = 4
NLM_F_ECHO = 8
NLM_F_DUMP_INTR = 16
NLM_F_DUMP_FILTERED = 32

NLM_F_ROOT = 0x100
NLM_F_MATCH = 0x200
NLM_F_ATOMIC = 0x400
NLM_F_DUMP = NLM_F_ROOT | NLM_F_MATCH

NLM_F_REPLACE = 0x100
NLM_F_EXCL = 0x200
NLM_F_CREATE = 0x400
NLM_F_APPEND = 0x800

NLM_F_NONREC = 0x100

NLM_F_CAPPED = 0x100
NLM_F_ACK_TLVS = 0x200

NLMSG_NOOP = 1
NLMSG_ERROR = 2
NLMSG_DONE = 3
NLMSG_OVERRUN = 4
NLMSG_MIN_TYPE = 16

NLMSGERR_ATTR_UNUSED = 0
NLMSGERR_ATTR_MSG = 1
NLMSGERR_ATTR_OFFS = 2
NLMSGERR_ATTR_COOKIE = 3
NLMSGERR_ATTR_POLICY = 4

NETLINK_ADD_MEMBERSHIP = 1
NETLINK_DROP_MEMBERSHIP = 2
NETLINK_PKTINFO = 3
NETLINK_BROADCAST_ERROR = 4
NETLINK_NO_ENOBUFS = 5
NETLINK_LISTEN_ALL_NSID = 8
NETLINK_LIST_MEMBERSHIPS = 9
NETLINK_CAP_ACK = 10
NETLINK_EXT_ACK = 11
NETLINK_GET_STRICT_CHK = 12

SOL_NETLINK = 270


class NetlinkMessage:
	def __init__(self, type, flags, payload):
		self.type = type
		self.flags = flags
		self.payload = payload


class NetlinkSocket:
	def __init__(self, s):
		self.s = s
		self.pid = s.getsockname()[0]
		
		self.sequence = itertools.count(1)
		self.pending = {}
		self.replies = {}
		self.packets = {}
		
		self.send_channel, self.recv_channel = trio.open_memory_channel(math.inf)
	
	def __enter__(self): return self
	def __exit__(self, typ, val, tb):
		self.send_channel.close()
	
	async def start(self):
		while True:
			data = await self.s.recv(65536)
			
			while data:
				length, type, flags, sequence, pid = struct.unpack_from("IHHII", data)
				payload = data[16:length]
				
				message = NetlinkMessage(type, flags, payload)
				if type == NLMSG_ERROR or type == NLMSG_DONE:
					if sequence in self.pending:
						self.replies[sequence] = message
						self.pending.pop(sequence).set()
					else:
						logger.warning("Received unexpected ack or error packet")
				elif sequence == 0:
					await self.send_channel.send(message)
				elif sequence in self.packets:
					self.packets[sequence].append(message)
				else:
					logger.warning("Received packet with unexpected sequence: %i" %sequence)
				
				data = data[length:]
	
	async def send(self, data):
		await self.s.send(data)
	
	async def receive(self):
		return await self.recv_channel.receive()
	
	async def request(self, type, payload=b"", flags=0):
		event = trio.Event()
		
		sequence = next(self.sequence)
		self.pending[sequence] = event
		self.packets[sequence] = []
		
		flags |= NLM_F_REQUEST | NLM_F_ACK
		
		length = 16 + len(payload)
		header = struct.pack("IHHII", length, type, flags, sequence, self.pid)
		await self.send(header + payload)
		
		await event.wait()
		
		response = self.replies.pop(sequence)
		if response.type == NLMSG_ERROR:
			code = struct.unpack_from("i", response.payload)[0]
			if code != 0:
				raise OSError(-code, os.strerror(-code))
		elif response.type != NLMSG_DONE:
			raise RuntimeError("Expected ack or error packet")
		
		return self.packets.pop(sequence)
	
	async def noop(self):
		await self.request(NLMSG_NOOP)


@contextlib.asynccontextmanager
async def connect(family):
	s = trio.socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM, family)
	with s:
		s.setsockopt(SOL_NETLINK, NETLINK_CAP_ACK, True)
		
		await s.bind((0, 0))
		sock = NetlinkSocket(s)
		async with trio.open_nursery() as nursery:
			nursery.start_soon(sock.start)
			yield sock
			nursery.cancel_scope.cancel()
