
import struct


class StreamOut:
	def __init__(self):
		self.data = bytearray()
		self.pos = 0
	
	def get(self): return bytes(self.data)
	def size(self): return len(self.data)
	def tell(self): return self.pos
	def seek(self, pos):
		if pos > len(self.data):
			self.data += bytes(pos - len(self.data))
		self.pos = pos
	def skip(self, num): self.seek(self.pos + num)
	def align(self, num): self.skip((num - self.pos % num) % num)
	def available(self): return len(self.data) - self.pos
	def eof(self): return self.pos >= len(self.data)
		
	def write(self, data):
		self.data[self.pos : self.pos + len(data)] = data
		self.pos += len(data)
		
	def pad(self, num, char=b"\0"):
		self.write(char * num)
		
	def u8(self, value): self.write(bytes([value]))
	def u16(self, value): self.write(struct.pack("H", value))
	def u32(self, value): self.write(struct.pack("I", value))
	def u64(self, value): self.write(struct.pack("Q", value))
	
	def s8(self, value): self.write(struct.pack("b", value))
	def s16(self, value): self.write(struct.pack("h", value))
	def s32(self, value): self.write(struct.pack("i", value))
	def s64(self, value): self.write(struct.pack("q", value))


class StreamIn:
	def __init__(self, data):
		self.data = data
		self.pos = 0
		
	def get(self): return self.data
	def size(self): return len(self.data)
	def tell(self): return self.pos
	def seek(self, pos):
		if pos > self.size():
			raise OverflowError("Buffer overflow")
		self.pos = pos
	def skip(self, num): self.seek(self.pos + num)
	def align(self, num): self.skip((num - self.pos % num) % num)
	def eof(self): return self.pos == len(self.data)
	def available(self): return len(self.data) - self.pos
	
	def peek(self, num):
		if self.available() < num:
			raise OverflowError("Buffer overflow")
		return self.data[self.pos : self.pos + num]
		
	def read(self, num):
		data = self.peek(num)
		self.skip(num)
		return data
		
	def readall(self):
		return self.read(self.available())
		
	def pad(self, num, char=b"\0"):
		if self.read(num) != char * num:
			raise ValueError("Incorrect padding")
	
	def u8(self): return self.read(1)[0]
	def u16(self): return struct.unpack("H", self.read(2))[0]
	def u32(self): return struct.unpack("I", self.read(4))[0]
	def u64(self): return struct.unpack("Q", self.read(8))[0]
	
	def s8(self): return struct.unpack("b", self.read(1))[0]
	def s16(self): return struct.unpack("h", self.read(2))[0]
	def s32(self): return struct.unpack("i", self.read(4))[0]
	def s64(self): return struct.unpack("q", self.read(8))[0]
