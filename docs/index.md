
## Welcome to python-netlink

This package provides an asynchronous [netlink](https://man7.org/linux/man-pages/man7/netlink.7.html) implementation based on [trio](https://github.com/python-trio/trio).

* [Features](#features)
* [Contributing](#contributing)
* [API Reference](#api-reference)

## Features
This package provides full support for the generic netlink controller (`nlctrl`) and basic support for [nl80211](https://wireless.wiki.kernel.org/en/developers/documentation/nl80211). Support for other netlink families can be added relatively easily.

Ideally, this Python package would be based on [anyio](https://github.com/agronholm/anyio) such that it supports [asyncio](https://docs.python.org/3/library/asyncio.html) applications as well. This isn't possible at the moment because anyio does not support raw sockets or `AF_NETLINK` yet, but maybe we will move to anyio in the future.

If you are looking for a synchronous library instead, check out [pyroute2](https://github.com/svinota/pyroute2).

## Contributing
Feel free to open a pull request or issue on [github](https://github.com/kinnay/python-netlink). Please try to follow the current code style as much as possible.

## API Reference
* [netlink](reference/netlink.md)
* [netlink.attributes](reference/attributes.md)
* [netlink.generic](reference/generic.md)
* [netlink.nl80211](reference/nl80211.md)
