# -*- encoding:utf8 -*-

import os, sys, platform, socket, json
from argparse import ArgumentParser
from bottle import Bottle, request, response, Response


__author__    = 'Kazuyuki TAKASE'
__copyright__ = 'PLEN Project Company Ltd., and all authors.'
__license__   = 'The MIT License'


# Create global instances.
# ==============================================================================
server = Bottle()
# from bottle import debug
# debug(True)

driver = None


# Set enable all requests CORS.
# ==============================================================================
@server.hook('after_request')
def enableCORS():
	response.headers['Access-Control-Allow-Origin']  = '*'
	response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
	response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


# Web API for "Output" command.
# ==============================================================================
@server.get("/output/<DEVICE>/<VALUE:int>")
def output(DEVICE, VALUE):
	data = {
		"command" : "Output",
		"device"  : DEVICE,
		"value"   : VALUE,
		"result"  : None
	}

	data["result"] = driver.output(DEVICE, VALUE)

	response = Response(json.dumps(data, sort_keys = True, indent = 4))
	response.mimetype = "server/json"

	return response


# Web API for "Play" command.
# ==============================================================================
@server.get("/play/<SLOT:int>")
def play(SLOT):
	data = {
		"command" : "Play",
		"slot"    : SLOT,
		"result"  : None
	}

	data["result"] = driver.play(SLOT)

	response = Response(json.dumps(data, sort_keys = True, indent = 4))
	response.mimetype = "server/json"

	return response


# Web API for "Stop" command.
# ==============================================================================
@server.get("/stop")
def stop():
	data = {
		"command" : "Stop",
		"result"  : None
	}

	data["result"] = driver.stop()

	response = Response(json.dumps(data, sort_keys = True, indent = 4))
	response.mimetype = "server/json"

	return response


# Web API for "Install" command.
# ==============================================================================
@server.post("/install")
def install():
	data = {
		"command" : "Install",
		"result"  : None
	}

	data["result"] = driver.install(request.json)

	response = Response(json.dumps(data, sort_keys = True, indent = 4))
	response.mimetype = "server/json"

	return response


# Web API for "Connect" command.
# ==============================================================================
@server.get("/connect")
def connect():
	data = {
		"command" : "Connect",
		"result"  : None
	}

	data["result"] = driver.connect()

	response = Response(json.dumps(data, sort_keys = True, indent = 4))
	response.mimetype = "server/json"

	return response


# Web API for "Disconnect" command.
# ==============================================================================
@server.get("/disconnect")
def disconnect():
	data = {
		"command" : "Disconnect",
		"result"  : None
	}

	data["result"] = driver.disconnect()

	response = Response(json.dumps(data, sort_keys = True, indent = 4))
	response.mimetype = "server/json"

	return response


# Application entry point.
# ==============================================================================
def main(args):
	# Get device map.
	if os.path.isfile('device_map.json'):
		with open('device_map.json', 'r') as fin:
			DEVICE_MAP = json.load(fin)
	else:
		print 'Error : "device_map.json" is not found!'
		print '==============================================================================='

		sys.exit()

	# Create a driver instance.
	global driver

	if args.driver == 'usb':
		import driver.usb.core as USBDriver
		driver = USBDriver.Core(DEVICE_MAP)

	if args.driver == 'bled112':
		if platform.system() != 'Windows':
			print 'Error : "BLED112Driver.Core" is not supported your OS!'
			print '==============================================================================='

			sys.exit()

		import driver.bled112.core as BLED112Driver
		driver = BLED112Driver.Core(DEVICE_MAP)

	if args.driver == 'ble':
		if platform.system() != 'Darwin':
			print 'Error : "BLEDriver.Core" is not supported your OS!'
			print '==============================================================================='

			sys.exit()

		print 'Error : "BLEDriver.Core" is not impremented! (Coming soon...)'
		print '==============================================================================='

		sys.exit()

	# Print server configurations.
	ip = socket.gethostbyname(socket.gethostname())
	print '"PLEN - Control Server" is on "%s:%d".' % (ip, args.port)

	if args.mac != '':
		print 'Connect only "%s".' % (args.mac)

	print '==============================================================================='
	sys.stdout.flush()

	# Run the HTTP Server. 
	server.run(host = 'localhost', port = args.port)


# Purse command-line option(s).
# ==============================================================================
if __name__ == "__main__":
	description = """
===============================================================================

/￣￣￣` 　|￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣|
|○　○| ＜　"PLEN - Control Server" is a HTTP server for controlling PLEN. |
+:----:+ 　|________________________________________________________________|
 ￣￣￣
===============================================================================
"""[1:-1]
	print description

	arg_parser = ArgumentParser()
	arg_parser.add_argument(
		'-p', '--port',
		dest    = 'port',
		type    = int,
		default = 17264,
		metavar = '<PORT NO.>',
		help    = 'default value is "17264".'
	)
	arg_parser.add_argument(
		'-d', '--driver',
		dest    = 'driver',
		choices = ('usb', 'bled112', 'ble'),
		default = 'usb',
		metavar = '<DRIVER>',
		help    = 'please choose "usb" (default), "bled112" (win only), or "ble" (mac only).'
	)
	arg_parser.add_argument(
		'--mac',
		dest    = 'mac',
		default = '',
		metavar = '<MAC ADDR.>',
		help    = "please set your PLEN's MAC address."
	)

	args = arg_parser.parse_args()
	main(args)