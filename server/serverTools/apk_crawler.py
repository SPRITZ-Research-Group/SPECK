import requests
from bs4 import BeautifulSoup
from subprocess import call
import sys
import processRequest

BASE_URL = "https://apkpure.com/app/"
PREFIX_DOWNLOAD_URL = "https://apkpure.com"
SUFFIX_DOWNLOAD_URL = 'download?from=details';
WEBSITE = "apkpure.com"

DOWNLOAD_URL = 'https://download.apkpure.com/b/apk/'
DOWNLOAD_URL2 = 'https://download.apkpure.com/b/xapk/'
KEYWORD = "download"

class Downloader():
	def __init__(self, timeout, ip, port):
		self.error_msg = ""
		self.timeout = timeout
		self.ip = ip
		self.port = port

	def errorOccurred(self):
		return (self.error_msg != "")

	def getError(self):
		return self.error_msg

	def download_file(self, s, pkg, url, server):
		if (not server.broken_pipe()):
			print("\033[90m[%%] (%s:%s) >> Downloading of %s\033[0m" % (self.ip, self.port, pkg))
			try:
				apk_res = s.get(url, timeout=self.timeout)
			except:
				self.error_msg = "error=Server interrupted"
				return

			if apk_res.status_code != 200:
				self.error_msg = "error=App" + pkg + "not found on " + BASE_URL

			fname = processRequest.download_directory + '/' + pkg + ".apk"
			fo = open(fname, "wb")
			fo.write(apk_res.content)
			fo.close()

			print("\033[90m[%%] (%s:%s) << Download completed for '%s'\033[0m" % (self.ip, self.port, pkg))
		else:
			print("\033[93m[!] (%s:%s) Download of %s was canceled\033[0m" % (self.ip, self.port, pkg))

	def get_links(self, s, url):
		try:
			initial_res = s.get(url, timeout=self.timeout)
		except:
			self.error_msg = "error=Server interupted"
			return

		if initial_res.status_code != 200:
			self.error_msg = "error=App version not available on " + BASE_URL

		initial_soup = BeautifulSoup(initial_res.content, 'html.parser')
		all_links = [x.get('href') for x in initial_soup.find_all('a')]

		return all_links

	def APK_crawler_latest(self, pkg, server):
		server.keep_client_update("Checking app availability", 2)

		s = requests.Session();

		all_links = self.get_links(s, BASE_URL + pkg)
		if (self.errorOccurred()):
			return

		url = ""
		# Search for the latest version
		for x in all_links:
			if (not x is None) and (pkg in x) and (SUFFIX_DOWNLOAD_URL in x):
				url = PREFIX_DOWNLOAD_URL + x
				#print('[LATEST VERSION FOUND] ============> ' + url)
				break

		if (url != ""):
			all_links = self.get_links(s, url)
			if (self.errorOccurred()):
				return

			for x in all_links:
				if (not x is None) and (DOWNLOAD_URL in x or DOWNLOAD_URL2 in x):
					print("[*] (%s:%s) << Link found for %s: %s" % (self.ip, self.port, pkg, x))
					self.download_file(s, pkg, x, server)
					return
		
		self.error_msg = "error=App not found on " + BASE_URL
		

	def find_version(self, s, pkg, version, link):
		try:
			initial_res = s.get(link, timeout=self.timeout)
		except:
			self.error_msg = "error=Server interupted"
			return

		if initial_res.status_code != 200:
			self.error_msg = "error=App not found on " + BASE_URL

		initial_soup = BeautifulSoup(initial_res.content, 'html.parser')

		url = ""
		# Search for the right version number
		for x in initial_soup.find_all('a'):
			link = x.get('href')
			title = x.get('title')

			vsn = version + ' '
			if (not link is None) and (not title is None) and (pkg in link) and (KEYWORD in link) and (vsn in title):
				#print('[VERSION %s FOUND] ============> %s' % (version, x.get('href')))
				url = PREFIX_DOWNLOAD_URL + x.get('href')
				break

		return url

	def APK_crawler_version(self, pkg, version, server):
		server.keep_client_update("Checking app availability", 2)
		
		s = requests.Session();
		url = self.find_version(s, pkg, version, BASE_URL + pkg)
		if (self.errorOccurred()):
			return

		if (url == ""):
			url = self.find_version(s, pkg, version, BASE_URL + pkg + '/versions')
			if (self.errorOccurred()):
				return

		if (url != ""):
			all_links = self.get_links(s, url)
			if (self.errorOccurred()):
				return

			for x in all_links:
				if (not x is None) and (DOWNLOAD_URL in x or DOWNLOAD_URL2 in x):
					print("[*] (%s:%s) << Link found for %s: %s" % (self.ip, self.port, pkg, x))
					self.download_file(s, pkg, x, server)
					return
		
		self.error_msg = "error=App version not available on " + BASE_URL


	def APK_crawler(self, server, pkg, version=""):
		if (version == ""):
			self.APK_crawler_latest(pkg, server)
		else:
			self.APK_crawler_version(pkg, version, server)


if __name__ == '__main__':
	pkg = 'com.facebook.lite'
	version = '86.0.0.9.190'

	dwl = Downloader()
	dwl.APK_crawler(pkg, version)

	if (dwl.errorOccurred()):
		print("[ERROR] ", dwl.getError())







