
from netlink import attributes
import netlink

import contextlib
import struct


RTM_NEWADDR = 20
RTM_NEWNEIGH = 28
RTM_DELNEIGH = 29

IFA_UNSPEC = 0
IFA_ADDRESS = 1
IFA_LOCAL = 2
IFA_LABEL = 3
IFA_BROADCAST = 4
IFA_ANYCAST = 5
IFA_CACHEINFO = 6
IFA_MULTICAST = 7
IFA_FLAGS = 8
IFA_RT_PRIORITY = 9
IFA_TARGET_NETNSID = 10

NDA_UNSPEC = 0
NDA_DST = 1
NDA_LLADDR = 2
NDA_CACHEINFO = 3
NDA_PROBES = 4
NDA_VLAN = 5
NDA_PORT = 6
NDA_VNI = 7
NDA_IFINDEX = 8
NDA_MASTER = 9
NDA_LINK_NETNSID = 10
NDA_SRC_VNI = 11
NDA_PROTOCOL = 12
NDA_NH_ID = 13
NDA_FDB_EXT_ATTRS = 14
NDA_FLAGS_EXT = 15

NFEA_UNSPEC = 0
NFEA_ACTIVITY_NOTIFY = 1
NFEA_DONT_REFRESH = 2

IFA_F_SECONDARY = 1
IFA_F_TEMPORARY = IFA_F_SECONDARY

IFA_F_NODAD = 2
IFA_F_OPTIMISTIC = 4
IFA_F_DADFAILED = 8
IFA_F_HOMEADDRESS = 16
IFA_F_DEPRECATED = 32
IFA_F_TENTATIVE = 64
IFA_F_PERMANENT = 128
IFA_F_MANAGETEMPADDR = 256
IFA_F_NOPREFIXROUTE = 512
IFA_F_MCAUTOJOIN = 1024
IFA_F_STABLE_PRIVACY = 2048

NTF_USE = 1 << 0
NTF_SELF = 1 << 1
NTF_MASTER = 1 << 2
NTF_PROXY = 1 << 3
NTF_EXT_LEARNED = 1 << 4
NTF_OFFLOADED = 1 << 5
NTF_STICKY = 1 << 6
NTF_ROUTER = 1 << 7

NTF_EXT_MANAGED = 1 << 0

NUD_INCOMPLETE = 1
NUD_REACHABLE = 2
NUD_STALE = 4
NUD_DELAY = 8
NUD_PROBE = 16
NUD_FAILED = 32
NUD_NOARP = 64
NUD_PERMANENT = 128
NUD_NONE = 0

RT_SCOPE_UNIVERSE = 0
RT_SCOPE_SITE = 200
RT_SCOPE_LINK = 253
RT_SCOPE_HOST = 254
RT_SCOPE_NOWHERE = 255


ATTRIBUTES_IFA = {
	IFA_ADDRESS: attributes.binary(),
	IFA_LOCAL: attributes.binary(),
	IFA_LABEL: attributes.string(),
	IFA_BROADCAST: attributes.binary(),
	IFA_ANYCAST: attributes.binary(),
	IFA_CACHEINFO: attributes.binary(),
	IFA_MULTICAST: attributes.binary(),
	IFA_FLAGS: attributes.u32(),
	IFA_RT_PRIORITY: attributes.u32(),
	IFA_TARGET_NETNSID: attributes.s32()
}

ATTRIBUTES_NFEA = {
	NFEA_ACTIVITY_NOTIFY: attributes.u8(),
	NFEA_DONT_REFRESH: attributes.flag()
}

ATTRIBUTES_NDA = {
	NDA_DST: attributes.binary(),
	NDA_LLADDR: attributes.binary(),
	NDA_CACHEINFO: attributes.binary(),
	NDA_PROBES: attributes.u32(),
	NDA_VLAN: attributes.u16(),
	NDA_PORT: attributes.u16(),
	NDA_VNI: attributes.u32(),
	NDA_IFINDEX: attributes.u32(),
	NDA_MASTER: attributes.u32(),
	NDA_LINK_NETNSID: attributes.s32(),
	NDA_SRC_VNI: attributes.u32(),
	NDA_PROTOCOL: attributes.u8(),
	NDA_NH_ID: attributes.u32(),
	NDA_FDB_EXT_ATTRS: attributes.nested(ATTRIBUTES_NFEA),
	NDA_FLAGS_EXT: attributes.u32()
}


class RouteController:
	def __init__(self, netlink):
		self.netlink = netlink
	
	async def add_address(self, family, prefix, flags, scope, index, attrs):
		payload = struct.pack("BBBBI", family, prefix, flags, scope, index)
		payload += attributes.encode(attrs, ATTRIBUTES_IFA)
		flags = netlink.NLM_F_CREATE | netlink.NLM_F_EXCL
		await self.netlink.request(RTM_NEWADDR, payload, flags)
	
	async def add_neighbor(self, family, index, state, flags, type, attrs):
		payload = struct.pack("B3xiHBB", family, index, state, flags, type)
		payload += attributes.encode(attrs, ATTRIBUTES_NDA)
		flags = netlink.NLM_F_CREATE | netlink.NLM_F_EXCL
		await self.netlink.request(RTM_NEWNEIGH, payload, flags)
	
	async def remove_neighbor(self, family, index, state, flags, type, attrs):
		payload = struct.pack("B3xiHBB", family, index, state, flags, type)
		payload += attributes.encode(attrs, ATTRIBUTES_NDA)
		await self.netlink.request(RTM_DELNEIGH, payload, 0)


@contextlib.asynccontextmanager
async def connect():
	async with netlink.connect(netlink.NETLINK_ROUTE) as sock:
		yield RouteController(sock)
