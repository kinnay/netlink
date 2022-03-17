
# Module: <code>netlink.route</code>
Provides a limited implementation of [rtnetlink](https://man7.org/linux/man-pages/man7/rtnetlink.7.html).

<code>**class** [RouteController](#routecontroller)</code><br>
<span class="docs">Implements rtnetlink functions.</span>

<code>**async with** connect() -> [RouteController](#routecontroller)</code><br>
<span class="docs">Creates a netlink socket for rtnetlink.</span>

## RouteController
<code>**async def add_address**(family: int, prefix: int, flags: int, scope: int, index: int, attrs: dict[int, object]) -> None</code><br>
<span class="docs">Associates an IP address with the given interface (`RTM_NEWADDR`).</span>

<code>**async def add_neighbor**(family: int, index: int, state: int, flags: int, type: int, attrs: dict[int, object]) -> None</code><br>
<span class="docs">Adds a neighbor table entry (`RTM_NEWNEIGH`).</span>

<code>**async def remove_neighbor**(family: int, index: int, state: int, flags: int, type: int, attrs: dict[int, object]) -> None</code><br>
<span class="docs">Removes a neighbor table entry (`RTM_DELNEIGH`).</span>
