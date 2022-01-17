
from netlink import streams
import struct


NLA_F_NESTED = 1 << 15
NLA_F_NET_BYTEORDER = 1 << 14
NLA_TYPE_MASK = ~(NLA_F_NESTED | NLA_F_NET_BYTEORDER)

NL_ATTR_TYPE_INVALID = 0
NL_ATTR_TYPE_FLAG = 1
NL_ATTR_TYPE_U8 = 2
NL_ATTR_TYPE_U16 = 3
NL_ATTR_TYPE_U32 = 4
NL_ATTR_TYPE_U64 = 5
NL_ATTR_TYPE_S8 = 6
NL_ATTR_TYPE_S16 = 7
NL_ATTR_TYPE_S32 = 8
NL_ATTR_TYPE_S64 = 9
NL_ATTR_TYPE_BINARY = 10
NL_ATTR_TYPE_STRING = 11
NL_ATTR_TYPE_NUL_STRING = 12
NL_ATTR_TYPE_NESTED = 13
NL_ATTR_TYPE_NESTED_ARRAY = 14
NL_ATTR_TYPE_BITFIELD32 = 15

NL_POLICY_TYPE_ATTR_UNSPEC = 0
NL_POLICY_TYPE_ATTR_TYPE = 1
NL_POLICY_TYPE_ATTR_MIN_VALUE_S = 2
NL_POLICY_TYPE_ATTR_MAX_VALUE_S = 3
NL_POLICY_TYPE_ATTR_MIN_VALUE_U = 4
NL_POLICY_TYPE_ATTR_MAX_VALUE_U = 5
NL_POLICY_TYPE_ATTR_MIN_LENGTH = 6
NL_POLICY_TYPE_ATTR_MAX_LENGTH = 7
NL_POLICY_TYPE_ATTR_POLICY_IDX = 8
NL_POLICY_TYPE_ATTR_POLICY_MAXTYPE = 9
NL_POLICY_TYPE_ATTR_BITFIELD32_MASK = 10
NL_POLICY_TYPE_ATTR_PAD = 11
NL_POLICY_TYPE_ATTR_MASK = 12


class AttributeType:
	U8 = 0
	U16 = 1
	U32 = 2
	U64 = 3
	
	S8 = 4
	S16 = 5
	S32 = 6
	S64 = 7
	
	BINARY = 8
	STRING = 9
	
	NESTED = 10
	ARRAY = 11
	DICT = 12
	
	FLAG = 13
	PADDING = 14
	
	
	def __init__(self, type, *, base=0, etype=None, map=None):
		self.type = type
		self.base = base
		self.etype = etype
		self.map = map
	
	def encode(self, value):
		if self.type == AttributeType.U8: return struct.pack("B", value)
		elif self.type == AttributeType.U16: return struct.pack("H", value)
		elif self.type == AttributeType.U32: return struct.pack("I", value)
		elif self.type == AttributeType.U64: return struct.pack("Q", value)
		
		elif self.type == AttributeType.S8: return struct.pack("b", value)
		elif self.type == AttributeType.S16: return struct.pack("h", value)
		elif self.type == AttributeType.S32: return struct.pack("i", value)
		elif self.type == AttributeType.S64: return struct.pack("q", value)
		
		elif self.type == AttributeType.BINARY: return value
		elif self.type == AttributeType.STRING: return value.encode() + b"\0"
		
		elif self.type == AttributeType.NESTED: return encode(value, self.map)
		elif self.type == AttributeType.ARRAY:
			attrs = {i + self.base: self.etype.encode(item) for i, item in enumerate(value)}
			return encode_raw(attrs)
		elif self.type == AttributeType.DICT:
			attrs = {key: self.etype.encode(val) for key, val in value.items()}
			return encode_raw(attrs)
		
		elif self.type == AttributeType.FLAG: return b""
		elif self.type == AttributeType.PADDING: return b""
		
		else:
			raise ValueError("Invalid attribute type: %i" %self.type)
	
	def decode(self, data):
		if self.type == AttributeType.U8: return data[0]
		elif self.type == AttributeType.U16: return struct.unpack("H", data)[0]
		elif self.type == AttributeType.U32: return struct.unpack("I", data)[0]
		elif self.type == AttributeType.U64: return struct.unpack("Q", data)[0]
		
		elif self.type == AttributeType.S8: return struct.unpack("b", data)[0]
		elif self.type == AttributeType.S16: return struct.unpack("h", data)[0]
		elif self.type == AttributeType.S32: return struct.unpack("i", data)[0]
		elif self.type == AttributeType.S64: return struct.unpack("q", data)[0]
		
		elif self.type == AttributeType.BINARY: return data
		elif self.type == AttributeType.STRING: return data.decode().rstrip("\0")
		
		elif self.type == AttributeType.NESTED: return decode(data, self.map)
		elif self.type == AttributeType.ARRAY:
			return [self.etype.decode(val) for val in decode_raw(data).values()]
		elif self.type == AttributeType.DICT:
			return {key: self.etype.decode(val) for key, val in decode_raw(data).items()}
		
		elif self.type == AttributeType.FLAG: return True
		elif self.type == AttributeType.PADDING: return b""
		
		else:
			raise ValueError("Invalid attribute type: %i" %self.type)


def u8(): return AttributeType(AttributeType.U8)
def u16(): return AttributeType(AttributeType.U16)
def u32(): return AttributeType(AttributeType.U32)
def u64(): return AttributeType(AttributeType.U64)

def s8(): return AttributeType(AttributeType.S8)
def s16(): return AttributeType(AttributeType.S16)
def s32(): return AttributeType(AttributeType.S32)
def s64(): return AttributeType(AttributeType.S64)

def binary(): return AttributeType(AttributeType.BINARY)
def string(): return AttributeType(AttributeType.STRING)

def nested(map): return AttributeType(AttributeType.NESTED, map=map)
def array(etype, *, base=0): return AttributeType(AttributeType.ARRAY, etype=etype, base=base)
def dict(etype): return AttributeType(AttributeType.DICT, etype=etype)

def flag(): return AttributeType(AttributeType.FLAG)
def padding(): return AttributeType(AttributeType.PADDING)


def encode_raw(attributes):
	stream = streams.StreamOut()
	for key, value in attributes.items():
		stream.u16(len(value) + 4)
		stream.u16(key)
		stream.write(value)
		stream.align(4)
	return stream.get()

def encode(attributes, typemap):
	attributes = attributes.copy()
	for key in attributes:
		if key not in typemap:
			raise ValueError("Unknown attribute: %i" %key)
		attributes[key] = typemap[key].encode(attributes[key])
	return encode_raw(attributes)

def decode_raw(data):
	attributes = {}
	stream = streams.StreamIn(data)
	while not stream.eof():
		size = stream.u16()
		key = stream.u16() & NLA_TYPE_MASK
		attributes[key] = stream.read(size - 4)
		stream.align(4)
	return attributes

def decode(data, typemap):
	attributes = decode_raw(data)
	for key in attributes:
		if key not in typemap:
			raise ValueError("Unknown attribute: %i" %key)
		attributes[key] = typemap[key].decode(attributes[key])
	return attributes


class Policy:
	def __init__(self, attributes):
		self.type = attributes[NL_POLICY_TYPE_ATTR_TYPE]
		
		self.policy_id = attributes.get(NL_POLICY_TYPE_ATTR_POLICY_IDX)
		self.policy_maxtype = attributes.get(NL_POLICY_TYPE_ATTR_POLICY_MAXTYPE)
		self.min_length = attributes.get(NL_POLICY_TYPE_ATTR_MIN_LENGTH)
		self.max_length = attributes.get(NL_POLICY_TYPE_ATTR_MAX_LENGTH)
		
		self.min_value = None
		self.max_value = None
		self.mask = None
		
		if self.type in [NL_ATTR_TYPE_U8, NL_ATTR_TYPE_U16, NL_ATTR_TYPE_U32, NL_ATTR_TYPE_U64]:
			self.min_value = attributes[NL_POLICY_TYPE_ATTR_MIN_VALUE_U]
			self.max_value = attributes[NL_POLICY_TYPE_ATTR_MAX_VALUE_U]
			self.mask = attributes.get(NL_POLICY_TYPE_ATTR_MASK)
		elif self.type in [NL_ATTR_TYPE_S8, NL_ATTR_TYPE_S16, NL_ATTR_TYPE_S32, NL_ATTR_TYPE_S64]:
			self.min_value = attributes[NL_POLICY_TYPE_ATTR_MIN_VALUE_S]
			self.max_value = attributes[NL_POLICY_TYPE_ATTR_MAX_VALUE_S]
		elif self.type == NL_ATTR_TYPE_BITFIELD32:
			self.mask = attributes[NL_POLICY_TYPE_ATTR_BITFIELD32_MASK]


ATTRIBUTES_POLICY_TYPE = {
	NL_POLICY_TYPE_ATTR_TYPE: u32(),
	NL_POLICY_TYPE_ATTR_MIN_VALUE_S: s64(),
	NL_POLICY_TYPE_ATTR_MAX_VALUE_S: s64(),
	NL_POLICY_TYPE_ATTR_MIN_VALUE_U: u64(),
	NL_POLICY_TYPE_ATTR_MAX_VALUE_U: u64(),
	NL_POLICY_TYPE_ATTR_MIN_LENGTH: u32(),
	NL_POLICY_TYPE_ATTR_MAX_LENGTH: u32(),
	NL_POLICY_TYPE_ATTR_POLICY_IDX: u32(),
	NL_POLICY_TYPE_ATTR_POLICY_MAXTYPE: u32(),
	NL_POLICY_TYPE_ATTR_BITFIELD32_MASK: u32(),
	NL_POLICY_TYPE_ATTR_PAD: padding(),
	NL_POLICY_TYPE_ATTR_MASK: u64()
}
