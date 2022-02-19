
# Module: <code>netlink</code>
Provides a basic implementation of the netlink protocol.

<code>**class** [NetlinkMessage](#netlinkmessage)</code><br>
<span class="docs">A simple class that holds a netlink message.</span>

<code>**class** [NetlinkSocket](#netlinksocket)</code><br>
<span class="docs">A socket that implements the netlink protocol.</span>

<code>**async with** connect(family: int) -> [NetlinkSocket](#netlinksocket)</code><br>
<span class="docs">Creates an `AF_NETLINK` socket for the given [family](#netlink-families).</span>

## Netlink Families
<span class="docs">
`NETLINK_ROUTE = 0`<br>
`NETLINK_UNUSED = 1`<br>
`NETLINK_USERSOCK = 2`<br>
`NETLINK_FIREWALL = 3`<br>
`NETLINK_SOCK_DIAG = 4`<br>
`NETLINK_NFLOG = 5`<br>
`NETLINK_XFRM = 6`<br>
`NETLINK_SELINUX = 7`<br>
`NETLINK_ISCSI = 8`<br>
`NETLINK_AUDIT = 9`<br>
`NETLINK_FIB_LOOKUP = 10`<br>
`NETLINK_CONNECTOR = 11`<br>
`NETLINK_NETFILTER = 12`<br>
`NETLINK_IP6_FW = 13`<br>
`NETLINK_DNRTMSG = 14`<br>
`NETLINK_KOBJECT_UEVENT = 15`<br>
`NETLINK_GENERIC = 16`<br>
`NETLINK_SCSITRANSPORT = 18`<br>
`NETLINK_ECRYPTFS = 19`<br>
`NETLINK_RDMMA = 20`<br>
`NETLINK_CRYPTO = 21`<br>
`NETLINK_SMC = 22`

`NETLINK_INET_DIAG = NETLINK_SOCK_DIAG`
</span>

## Netlink Flags
<span class="docs">
`NLM_F_REQUEST = 1`<br>
`NLM_F_MULTI = 2`<br>
`NLM_F_ACK = 4`<br>
`NLM_F_ECHO = 8`<br>
`NLM_F_DUMP_INTR = 16`<br>
`NLM_F_DUMP_FILTERED = 32`

`NLM_F_ROOT = 0x100`<br>
`NLM_F_MATCH = 0x200`<br>
`NLM_F_ATOMIC = 0x400`<br>
`NLM_F_DUMP = NLM_F_ROOT | NLM_F_MATCH`

`NLM_F_REPLACE = 0x100`<br>
`NLM_F_EXCL = 0x200`<br>
`NLM_F_CREATE = 0x400`<br>
`NLM_F_APPEND = 0x800`

`NLM_F_NONREC = 0x100`

`NLM_F_CAPPED = 0x100`<br>
`NLM_F_ACK_TLVS = 0x200`
</span>

## Message Types
<span class="docs">
`NLMSG_NOOP = 1`<br>
`NLMSG_ERROR = 2`<br>
`NLMSG_DONE = 3`<br>
`NLMSG_OVERRUN = 4`<br>
`NLMSG_MIN_TYPE = 16`
</span>

## NetlinkMessage
`type: int`<br>
`flags: int`<br>
`payload: bytes`

## NetlinkSocket
<code>**def add_membership**(id: int) ->  None</code><br>
<span class="docs">Adds the netlink socket to a multicast group.</span>

<code>**async def request**(type: int, payload: bytes = b"", flags: int = 0) -> list[[NetlinkMessage](#netlinkmessage)]</code><br>
<span class="docs">Sends a netlink request to the kernel and waits for an acknowledgement. The `flags` argument can be used to specify additional [flags](#netlink-flags) (e.g. `NLM_F_DUMP`). The flags `NLM_F_REQUEST` and `NLM_F_ACK` are always added to the request automatically. Returns the messages that were received from the kernel with a matching sequence id. Raises `OSError` if the kernel returns an error code.</span>

<code>**async def receive**() -> [NetlinkMessage](#netlinkmessage)</code><br>
<span class="docs">Receives a netlink message from the kernel with sequence id 0.</span>

<code>**async def noop**()</code><br>
<span class="docs">Sends `NLMSG_NOOP` to the kernel and waits for acknowledgement. Basically, this method does nothing.</span>
