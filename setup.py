
import setuptools

description = \
	"Asynchronous netlink library"

long_description = description

setuptools.setup(
	name = "python-netlink",
	version = "0.0.3",
	description = description,
	long_description = long_description,
	author = "Yannik Marchand",
	author_email = "ymarchand@me.com",
	url = "https://github.com/kinnay/python-netlink",
	license = "GPLv3",
	platforms = ["Linux"],
	packages = ["netlink"],
	install_requires = ["trio"]
)
