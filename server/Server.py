#!/usr/bin/python3
 
import socket, threading, sys, select, os, argparse
sys.path.insert(0, 'serverTools/')
from processRequest import *

END_MSG = b'.....END'

class ClientThread(threading.Thread):
	def __init__(self, ip, port, clientsocket, timeout, flowdroid, platform):
		threading.Thread.__init__(self)
		self.stopevent = threading.Event()
		self.timeout = timeout
		self.flowdroid = flowdroid
		self.platform = platform

		sys.path.insert(0, 'codeAnalysis/')

		# Socket
		self.ip = ip
		self.port = port
		self.clientsocket = clientsocket
		self.clientsocket.settimeout(2)
		
		self.broken = False

		self.option = None
		self.pkg = None
		self.optionDir = None
		self.request = None

	def join(self, timeout=None):
		self.stopevent.set()

	# FETCH DATA FROM CLIENT SOCKET
	def get_data(self):
		data = END_MSG
		try:
			data = self.clientsocket.recv(4096)
		except:
			pass
		return data

	def keep_client_update(self, string, step):
		tosend = "status="+string+"&step="+str(step)+"\n"
		self.clientsocket.send(tosend.encode())

	def send_manifest(self, string):
		tosend = "manifest#" + string + "\n"
		self.clientsocket.send(tosend.encode())

	def isBroken(self):
		return self.broken

	def broken_pipe(self):
		if (not self.isBroken()):
			random = "justtocheck\n"
			nb_check = 500 # if nb is low, BrokenPipe is not detected in time
			try:
				for i in range(0, nb_check):
					data = self.clientsocket.send(random.encode())
			except:
				print("\033[93m[!] (%s:%s) Broken pipe \033[0m" % (self.ip, self.port))
				self.broken = True
				return True
			return False
		else:
			return True

	def apkIsSent(self, request):
		subRequest = request.split(b'\n')[0].decode()
		self.optionDir = None
		if "withAPK=true" in subRequest:
			self.option = True

			pkg = ""
			for elem in subRequest.split("&"):
				if elem.split("=")[0] == "packageName":
					pkg = elem.split("=")[1]

			print("[*] (%s:%s) >> Saving of %s" % (self.ip, self.port, pkg))
			self.optionDir = processRequest.download_directory + "/" + pkg + ".apk"
			if pkg != "":
				splitted = request.split(b'\n')
				del splitted[0]
				file = b'\n'.join(splitted)

				fo = open(self.optionDir, "wb")
				fo.write(file)
				fo.close()

				print("[*] (%s:%s) << Saving of %s is successful" % (self.ip, self.port, pkg))
			else:
				self.optionDir = None

		else:
			self.option = False

		return request.split(b'\n')[0].decode("utf-8")

	def displayFileDownloading(self, checkRequestWithOption, fileSize, currentDataSize, paddingSize, percentArray, client_request, data):
		# Init Messages
		if (checkRequestWithOption):
			if (b'fileSize=' in client_request and b'withAPK=' in client_request):
				self.request = client_request.split(b'\n')[0].decode("utf-8")
				print("\033[92m[*] (%s:%s) >> '%s'\033[0m" % (self.ip, self.port, self.request))

				if (b'withAPK=true' in client_request):
					# INIT DATA SAVING !
					self.option = True
					for elem in self.request.split("&"):
						if elem.split("=")[0] == "packageName":
							self.pkg = elem.split("=")[1]
					self.optionDir = processRequest.download_directory + "/" + self.pkg + ".apk"

					# SAVE FIRST DATA !
					splitted = client_request.split(b'\n')
					del splitted[0]
					file = b'\n'.join(splitted)
					fo = open(self.optionDir, "wb")
					fo.write(file)
					fo.close()

					# INIT DATA DISPLAYING !
					checkRequestWithOption = False
					fileSize = int(client_request.split(b'fileSize=')[1].split(b'&')[0].decode("utf-8"))
					paddingSize = len(client_request.split(b'\n')[0])
					client_request = b''
					print("\033[90m[%%] (%s:%s) >> APK downloading... 0%%\033[0m" % (self.ip, self.port))
				else:
					self.option = False
		
		# Display donwloading state
		else:
			# SAVE
			if (self.pkg != None):
				fo = open(self.optionDir, "ab")
				fo.write(client_request)
				fo.close()
				client_request = b''
			# DISPLAY
			percent = round(((currentDataSize - paddingSize)*100)/(fileSize+1), 0)
			if ((percent % 10 == 0) and (percent not in percentArray)):
				print("\033[90m[%%] (%s:%s) >> APK downloading... %d%%\033[0m" % (self.ip, self.port, percent))
				percentArray.append(percent)

		currentDataSize += len(data)

		return client_request, checkRequestWithOption, fileSize, currentDataSize, paddingSize, percentArray

	# MAIN
	def run(self):
		client_request = b''

		checkRequestWithOption = True
		fileSize = 0
		currentDataSize = 0
		paddingSize = 0
		percentArray = [0]
		try:
			# GET CLIENT REQUEST
			data = self.get_data()
			while (not self.stopevent.isSet() and data != b''):
				
				if self.option != False:
					client_request, checkRequestWithOption, fileSize, currentDataSize, paddingSize, percentArray = self.displayFileDownloading(checkRequestWithOption, fileSize, currentDataSize, paddingSize, percentArray, client_request, data)

				if (END_MSG in data):
					client_request += data.replace(END_MSG, b'')
					if self.option != False:
						client_request, checkRequestWithOption, fileSize, currentDataSize, paddingSize, percentArray = self.displayFileDownloading(checkRequestWithOption, fileSize, currentDataSize, paddingSize, percentArray, client_request, data)
					break
				# main loop
				client_request += data
				data = self.get_data()

			# PROCESS THE REQUEST
			if (self.request != None and (not self.stopevent.isSet())):
				self.request = self.request.replace("\n","")
				
				# SERVER PROCESS
				process = ProcessRequest(self.ip, self.port)
				process.parse_request(self.request)

				if not self.option:
					process.download_apk(self, self.timeout)

				directoryName = process.decompile_apk(self, self.timeout)
				tosend = process.analyse_code(self, directoryName, self.flowdroid, self.platform)

				# ANSWER TO THE CLIENT
				if (process.get_error() != ""):
					tosend =  process.get_error().encode()

				if (not self.broken_pipe()):
					self.clientsocket.send(tosend)
					print("\033[92m[*] (%s:%s) << Request Completed! \033[0m" % (self.ip, self.port))

		except ConnectionResetError:
			pass

		# CLOSE SOCKET
		self.clientsocket.close()


# MAIN
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Server for android app')
	parser.add_argument('-i','--ip', help="IP address", default="127.0.0.1")
	parser.add_argument('-p','--port', help="Port number", type=int, default=8888)
	parser.add_argument('-t','--timeout', help="Time before killing bash process", type=int, default=10000)
	parser.add_argument('-f','--flowdroid', help="Use FlowDroid to detect false positive / negative", action='store_true')
	parser.add_argument('-r','--platform', help="Android SDK platform folder")

	args = parser.parse_args()

	if args.flowdroid and args.platform is None:
		parser.error("--flowdroid requires --platform")

	port = args.port
	host = args.ip
	max_queue = 10

	tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	tcpsock.bind((host, port))

	print(f"\033[94m[+] Server is running at \033[1m{host}\033[0m \033[94m on port \033[1m{port} \033[0m")

	if not os.path.exists(download_directory):
 		os.makedirs(download_directory)

	threads = []

	try:
		while True:
			tcpsock.listen(max_queue)
			(clientsocket, (ip, port)) = tcpsock.accept()

			newthread = ClientThread(ip, port, clientsocket, args.timeout, args.flowdroid, args.platform)
			
			threads.append(newthread)
			newthread.start()

	except (KeyboardInterrupt):
		print("\n\033[94m[+] Exiting... \033[0m")

		for t in threads:
			t.join()

		sys.exit(0)






	