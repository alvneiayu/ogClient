import threading
import platform
import time
from enum import Enum
import json
import queue

if platform.system() == 'Linux':
	from src.linux import ogOperations

class ogResponses(Enum):
	BAD_REQUEST=0
	IN_PROGRESS=1
	OK=2

class ogRest():
	def __init__(self):
		self.msgqueue = queue.Queue(1000)

	def buildJsonResponse(self, idstr, content):
		data = { idstr :content }
		return json.dumps(data)

	def getResponse(self, response, idstr=None, content=None):
		msg = ''
		if response == ogResponses.BAD_REQUEST:
			msg = 'HTTP/1.0 400 Bad request'
		elif response == ogResponses.IN_PROGRESS:
			msg = 'HTTP/1.0 202 Accepted'
		elif response == ogResponses.OK:
			msg = 'HTTP/1.0 200 OK'
		else:
			return msg

		if not content == None:
			jsonmsg = self.buildJsonResponse(idstr, content)
			msg = msg + '\nContent-Type:application/json'
			msg = msg + '\nContent-Length:' + str(len(jsonmsg))
			msg = msg + '\n' + jsonmsg

		msg = msg + '\r\n\r\n'
		return msg

	def processOperation(self, op, URI, cmd, client):
		if ("poweroff" in URI):
			self.process_poweroff(client)
		elif ("reboot" in URI):
			self.process_reboot(client)
		elif ("probe" in URI):
			self.process_probe(client)
		elif ("shell/run" in URI):
			self.process_shellrun(client, cmd)
		elif ("shell/output" in URI):
			self.process_shellout(client)
		else:
			client.send(self.getResponse(ogResponses.BAD_REQUEST))

		return 0

	def process_reboot(self, client):
		# Rebooting thread
		def rebt():
			ogOperations.reboot()

		client.send(self.getResponse(ogResponses.IN_PROGRESS))
		client.disconnect()
		threading.Thread(target=rebt).start()

	def process_poweroff(self, client):
		# Powering off thread
		def pwoff():
			time.sleep(2)
			ogOperations.poweroff()

		client.send(self.getResponse(ogResponses.IN_PROGRESS))
		client.disconnect()
		threading.Thread(target=pwoff).start()

	def process_probe(self, client):
		client.send(self.getResponse(ogResponses.OK))

	def process_shellrun(self, client, cmd):
		if cmd == None:
			client.send(self.getResponse(ogResponses.BAD_REQUEST))
			return

		self.msgqueue.put(ogOperations.execCMD(cmd))
		client.send(self.getResponse(ogResponses.IN_PROGRESS))

	def process_shellout(self, client):
		if self.msgqueue.empty():
			client.send(self.getResponse(ogResponses.IN_PROGRESS, 'out', ''))
		else:
			out = self.msgqueue.get()
			client.send(self.getResponse(ogResponses.IN_PROGRESS, 'out', out))