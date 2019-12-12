import threading
import platform
import time

print(platform.system())

if platform.system() == 'Linux':
	from linux import ogOperations

class ogProcess():
	def processOperation(self, op, URI):
		if ("poweroff" in URI):
			self.process_poweroff()
		elif ("reboot" in URI):
			self.process_reboot()

	def process_reboot(self):
		# Rebooting thread
		def rebt():
			ogOperations.reboot()
		threading.Thread(target=rebt).start()

	def process_poweroff(self):
		# Powering off thread
		def pwoff():
			time.sleep(2)
			ogOperations.poweroff()
		threading.Thread(target=pwoff).start()
