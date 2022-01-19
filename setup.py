
import setuptools

description = \
	"Asynchronous netlink library for Python"

long_description = \
	"This is an asynchronous netlink library for Python, " \
	"including basic support for nl80211."

setuptools.setup(
	name = "python-netlink",
	version = "0.0.6",
	description = description,
	long_description = long_description,
	author = "Yannik Marchand",
	author_email = "ymarchand@me.com",
	url = "https://github.com/kinnay/netlink",
	license = "GPLv3",
	platforms = ["Linux"],
	packages = ["netlink"],
	install_requires = ["trio"]
)
