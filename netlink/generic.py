
from netlink import attributes
import contextlib
import netlink
import struct


GENL_ID_CTRL = netlink.NLMSG_MIN_TYPE
GENL_ID_VFS_DQUOT = netlink.NLMSG_MIN_TYPE + 1
GENL_ID_PMCRAID = netlink.NLMSG_MIN_TYPE + 2

GENL_ADMIN_PERM = 1
GENL_CMD_CAP_DO = 2
GENL_CMD_CAP_DUMP = 4
GENL_CMD_CAP_HASPOL = 8
GENL_UNS_ADMIN_PERM = 16

CTRL_CMD_UNSPEC = 0
CTRL_CMD_NEWFAMILY = 1
CTRL_CMD_DELFAMILY = 2
CTRL_CMD_GETFAMILY = 3
CTRL_CMD_NEWOPS = 4
CTRL_CMD_DELOPS = 5
CTRL_CMD_GETOPS = 6
CTRL_CMD_NEWMCAST_GRP = 7
CTRL_CMD_DELMCAST_GRP = 8
CTRL_CMD_GETMCAST_GRP = 9
CTRL_CMD_GETPOLICY = 10

CTRL_ATTR_UNSPEC = 0
CTRL_ATTR_FAMILY_ID = 1
CTRL_ATTR_FAMILY_NAME = 2
CTRL_ATTR_VERSION = 3
CTRL_ATTR_HDRSIZE = 4
CTRL_ATTR_MAXATTR = 5
CTRL_ATTR_OPS = 6
CTRL_ATTR_MCAST_GROUPS = 7
CTRL_ATTR_POLICY = 8
CTRL_ATTR_OP_POLICY = 9
CTRL_ATTR_OP = 10

CTRL_ATTR_OP_UNSPEC = 0
CTRL_ATTR_OP_ID = 1
CTRL_ATTR_OP_FLAGS = 2

CTRL_ATTR_MCAST_GRP_UNSPEC = 0
CTRL_ATTR_MCAST_GRP_NAME = 1
CTRL_ATTR_MCAST_GRP_ID = 2

CTRL_ATTR_POLICY_UNSPEC = 0
CTRL_ATTR_POLICY_DO = 1
CTRL_ATTR_POLICY_DUMP = 2


class Command:
	def __init__(self, attributes):
		self.id = attributes[CTRL_ATTR_OP_ID]
		self.flags = attributes[CTRL_ATTR_OP_FLAGS]


class MulticastGroup:
	def __init__(self, attributes):
		self.name = attributes[CTRL_ATTR_MCAST_GRP_NAME]
		self.id = attributes[CTRL_ATTR_MCAST_GRP_ID]


class Family:
	def __init__(self, attributes):
		self.id = attributes[CTRL_ATTR_FAMILY_ID]
		self.name = attributes[CTRL_ATTR_FAMILY_NAME]
		self.version = attributes[CTRL_ATTR_VERSION]
		self.hdrsize = attributes[CTRL_ATTR_HDRSIZE]
		self.maxattr = attributes[CTRL_ATTR_MAXATTR]
		self.commands = [Command(op) for op in attributes.get(CTRL_ATTR_OPS, [])]
		self.mcast_groups = [MulticastGroup(group) for group in attributes.get(CTRL_ATTR_MCAST_GROUPS, [])]


class CommandPolicy:
	def __init__(self, attributes):
		self.do = attributes.get(CTRL_ATTR_POLICY_DO)
		self.dump = attributes.get(CTRL_ATTR_POLICY_DO)


class Policy:
	def __init__(self):
		self.family_id = None
		self.policies = {}
		self.commands = {}
	
	def update(self, attributes):
		family_id = attributes[CTRL_ATTR_FAMILY_ID]
		if self.family_id is None:
			self.family_id = family_id
		elif self.family_id != family_id:
			raise ValueError("Received policy with mixed family ids")
		
		if CTRL_ATTR_OP_POLICY in attributes:
			for cmd, attrs in attributes[CTRL_ATTR_OP_POLICY].items():
				self.commands[cmd] = CommandPolicy(attrs)
		if CTRL_ATTR_POLICY in attributes:
			for index, policy in attributes[CTRL_ATTR_POLICY].items():
				if index not in self.policies:
					self.policies[index] = {}
				for attr, policy in policy.items():
					self.policies[index][attr] = attributes.Policy(policy)


class GenericNetlinkMessage:
	def __init__(self, family, flags, cmd, version, header, attributes):
		self.family = family
		self.flags = flags
		self.cmd = cmd
		self.version = version
		self.header = header
		self.attributes = attributes


class GenericNetlinkReceiver:
	def __init__(self, netlink):
		self.netlink = netlink
		self.messages = {}
	
	async def receive(self, family):
		if family not in self.messages:
			self.messages[family] = []
		
		while not self.messages[family]:
			message = await self.netlink.receive()
			if message.type not in self.messages:
				self.messages[message.type] = []
			self.messages[message.type].append(message)
		
		return self.messages[family].pop(0)
	
	async def request(self, type, payload, flags=0):
		return await self.netlink.request(type, payload, flags)


class GenericNetlinkSocket:
	ATTRIBUTES = {}
	
	def __init__(self, netlink, family):
		self.netlink = netlink
		self.family = family
	
	def parse_message(self, message):
		attroffs = (self.family.hdrsize + 3) & ~3
		
		cmd, version, _ = struct.unpack_from("BBH", message.payload)
		header = message.payload[4:4+self.family.hdrsize]
		attrs = attributes.decode(message.payload[4+attroffs:], self.ATTRIBUTES)
		return GenericNetlinkMessage(message.type, message.flags, cmd, version, header, attrs)
	
	async def receive(self):
		return self.parse_message(await self.netlink.receive(self.family.id))
	
	async def request(self, cmd, attrs={}, flags=0, header=b""):
		if len(header) != self.family.hdrsize:
			raise ValueError("Invalid header size")
		
		padding = (4 - (self.family.hdrsize % 4)) % 4
		payload = header + bytes(padding) + attributes.encode(attrs, self.ATTRIBUTES)
		
		header = struct.pack("BBH", cmd, self.family.version, 0)
		messages = await self.netlink.request(self.family.id, header + payload, flags)
		
		generic = []
		for message in messages:
			generic.append(self.parse_message(message))
		return generic


class GenericNetlinkController(GenericNetlinkSocket):
	ATTRIBUTES_OP = {
		CTRL_ATTR_OP_ID: attributes.u32(),
		CTRL_ATTR_OP_FLAGS: attributes.u32()
	}
	
	ATTRIBUTES_MCAST_GRP = {
		CTRL_ATTR_MCAST_GRP_NAME: attributes.string(),
		CTRL_ATTR_MCAST_GRP_ID: attributes.u32()
	}
	
	ATTRIBUTES_POLICY = {
		CTRL_ATTR_POLICY_DO: attributes.u32(),
		CTRL_ATTR_POLICY_DUMP: attributes.u32()
	}

	ATTRIBUTES = {
		CTRL_ATTR_FAMILY_ID: attributes.u16(),
		CTRL_ATTR_FAMILY_NAME: attributes.string(),
		CTRL_ATTR_VERSION: attributes.u32(),
		CTRL_ATTR_HDRSIZE: attributes.u32(),
		CTRL_ATTR_MAXATTR: attributes.u32(),
		CTRL_ATTR_OPS: attributes.array(attributes.nested(ATTRIBUTES_OP), base=1),
		CTRL_ATTR_MCAST_GROUPS: attributes.array(attributes.nested(ATTRIBUTES_MCAST_GRP), base=1),
		CTRL_ATTR_POLICY: attributes.dict(attributes.dict(attributes.nested(attributes.ATTRIBUTES_POLICY_TYPE))),
		CTRL_ATTR_OP_POLICY: attributes.dict(attributes.nested(ATTRIBUTES_POLICY)),
		CTRL_ATTR_OP: attributes.u32()
	}
	
	async def get(self, name, cls):
		family = await self.get_family_by_name(name)
		return cls(self.netlink, family)
	
	async def get_families(self):
		messages = await self.request(CTRL_CMD_GETFAMILY, flags=netlink.NLM_F_DUMP)
		return [Family(message.attributes) for message in messages]
	
	async def get_family_by_id(self, id):
		attrs = {
			CTRL_ATTR_FAMILY_ID: id
		}
		messages = await self.request(CTRL_CMD_GETFAMILY, attrs)
		return Family(messages[0].attributes)
	
	async def get_family_by_name(self, name):
		attrs = {
			CTRL_ATTR_FAMILY_NAME: name
		}
		messages = await self.request(CTRL_CMD_GETFAMILY, attrs)
		return Family(messages[0].attributes)

	async def get_policy(self, attrs):
		messages = await self.request(CTRL_CMD_GETPOLICY, attrs, netlink.NLM_F_DUMP)
		
		if not messages:
			return None
		
		policy = Policy()
		for message in messages:
			policy.update(message.attributes)
		return policy

	async def get_policy_by_id(self, id, cmd=None):
		attrs = {
			CTRL_ATTR_FAMILY_ID: id
		}
		if cmd is not None: attrs[CTRL_ATTR_OP] = cmd
		return await self.get_policy(attrs)
	
	async def get_policy_by_name(self, name, cmd=None):
		attrs = {
			CTRL_ATTR_FAMILY_NAME: name
		}
		if cmd is not None: attrs[CTRL_ATTR_OP] = cmd
		return await self.get_policy(attrs)


@contextlib.asynccontextmanager
async def connect():
	# Bootstrap
	family = Family({
		CTRL_ATTR_FAMILY_ID: GENL_ID_CTRL,
		CTRL_ATTR_FAMILY_NAME: "nlctrl",
		CTRL_ATTR_VERSION: 2,
		CTRL_ATTR_HDRSIZE: 0,
		CTRL_ATTR_MAXATTR: max(GenericNetlinkController.ATTRIBUTES),
	})
	
	async with netlink.connect(netlink.NETLINK_GENERIC) as sock:
		receiver = GenericNetlinkReceiver(sock)
		yield GenericNetlinkController(receiver, family)
