
# Module: <code>netlink.generic</code>
Provides an implementation of the generic netlink protocol.

<code>**class** [GenericNetlinkMessage](#genericnetlinkmessage)</code><br>
<span class="docs">A simple class that holds a generic netlink message.</span>

<code>**class** [GenericNetlinkSocket](#genericnetlinksocket)</code><br>
<span class="docs">Base class for generic netlink families.</span>

<code>**class** [GenericNetlinkController](#genericnetlinkcontroller)([GenericNetlinkSocket](#genericnetlinksocket))</code><br>
<span class="docs">Implements the `nlctrl` family. Can be used to access other families.</span>

<code>**class** [Command](#command)</code><br>
<code>**class** [MulticastGroup](#multicastgroup)</code><br>
<code>**class** [Family](#family)</code><br>
<code>**class** [CommandPolicy](#commandpolicy)</code><br>
<code>**class** [Policy](#policy)</code><br>
<span class="docs">These classes contain the response of netlink controller requests.</span> 

<code>**async with** connect() -> [GenericNetlinkController](#genericnetlinkcontroller)</code><br>
<span class="docs">Creates a generic nelink socket. Returns a generic netlink controller that can be used to instantiate other families.</span>

## Command Flags
<span class="docs">
`GENL_ADMIN_PERM = 1`<br>
`GENL_CMD_CAP_DO = 2`<br>
`GENL_CMD_CAP_DUMP = 4`<br>
`GENL_CMD_CAP_HASPOL = 8`<br>
`GENL_UNS_ADMIN_PERM = 16`
</span>

## GenericNetlinkMessage
`family: int`<br>
`flags: int`<br>
`cmd: int`<br>
`version: int`<br>
`header: bytes`<br>
`attributes: dict[int, object]`

## GenericNetlinkSocket
This class and its subclasses should not be instantiated directly. Instead, one should obtain an instance from <code>[GenericNetlinkController](#genericnetlinkcontroller).get()</code> or another function.

<code>**async def receive**() -> [GenericNetlinkMessage](#genericnetlinkmessage)</code><br>
<span class="docs">Receives a netlink message from the kernel for the netlink family that belongs to this socket.</span>

<code>**async def request**(cmd: int, attrs: dict[int, object], flags: int = 0, header: bytes = b"") -> list[[GenericNetlinkMessage](#genericnetlinkmessage)]</code><br>
<span class="docs">Sends a generic netlink request to the kernel and waits for an acknowledgement. The `flags` argument can be used to specify additional [flags](#netlink-flags) (e.g. `NLM_F_DUMP`). The flags `NLM_F_REQUEST` and `NLM_F_ACK` are always added to the request automatically. Returns the messages that were received from the kernel with a matching sequence id. Raises `OSError` if the kernel returns an error code.</span>

## GenericNetlinkController
This class inherits [`GenericNetlinkSocket`](#genericnetlinksocket). It provides a simple interface for `nlctrl` and can also be used to instantiate other netlink families.

<code>**async def get**(name: str, cls: Type[GenericNetlinkSocket](#genericnetlinksocket)) -> [GenericNetlinkSocket](#genericnetlinksocket)</code><br>
<span class="docs">Creates an instance of the given class and connects it to the given netlink family.</span>

<code>**async def get_families**() -> list[[Family](#family)]</code><br>
<span class="docs">Requests the list of generic netlink families that are provided by the kernel.</span>

<code>**async def get_family_by_id**(id: int) -> [Family](#family)</code><br>
<span class="docs">Requests information about a specific family by id.</span>

<code>**async def get_family_by_name**(name: str) -> [Family](#family)</code><br>
<span class="docs">Requests information about a specific family by name.</span>

<code>**async def get_policy_by_id**(id: int, cmd: int = None) -> [Policy](#policy)</code><br>
<span class="docs">Requests the policy for all commands of the given family id, or a specific command if `cmd` is given.</span>

<code>**async def get_policy_by_name**(name: str, cmd: int = None) -> [Policy](#policy)</code><br>
<span class="docs">Requests the policy for all commands of the given family name, or a specific command if `cmd` is given.</span>

## Command
`id: int`<br>
`flags: int`

## MulticastGroup
`name: str`<br>
`id: int`

## Family
`id: int`<br>
`name: str`<br>
`version: int`<br>
`hdrsize: int`<br>
`maxattr: int`<br>
<code>commands: list[[Command](#command)]</code><br>
<code>mcast_groups: list[[MulticastGroup](#multicastgroup)]</code>

## CommandPolicy
`do: int | None`<br>
`dump: int | None`

## Policy
<code>policies: dict[int, dict[int, [attributes.Policy](attributes.md#policy)]]</code><br>
<code>commands: dict[int, [CommandPolicy](#commandpolicy)]</code>

