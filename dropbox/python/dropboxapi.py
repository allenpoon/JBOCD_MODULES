# Include the Dropbox SDK
import sys
import dropbox
import ConfigParser

class DropboxAPI:
	def __init__(self, json, working_dir):
		Config = ConfigParser.ConfigParser()
		Config.read("/var/JBOCD/module/dropbox/config.ini")
		# Get your app key and secret from the Dropbox developer website
		app_key = self.ConfigSectionMap("dropbox", Config)['appkey']
		app_secret = self.ConfigSectionMap("dropbox", Config)['appsecret']

		self.drop = dropbox.client.DropboxClient(json)
		self.working_dir = working_dir;

		try:
			self.drop.file_create_folder(self.working_dir)
		except dropbox.rest.ErrorResponse as e:
			pass
		#print "working_dir=", self.working_dir
		
	def ConfigSectionMap(self, section, Config):
		dict1 = {}
		options = Config.options(section)
		for option in options:
			try:
				dict1[option] = Config.get(section, option)
				if dict1[option] == -1:
					DebugPrint("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
		return dict1

	def put(self, local, remote):
		try:
			f = open(local, 'rb')
			response = self.drop.put_file(self.working_dir + '/' + remote, f, True)
		except dropbox.rest.ErrorResponse as e:
			#print "Put Error: ", e.error_msg
			#print "\tStatus: ", e.status
			#print "\tReason: ", e.reason
			#print "\tuser_error_msg: ", e.user_error_msg
			return e.status
		return 0

	def get(self, remote, local):
		try:
			f, meta = self.drop.get_file_and_metadata(self.working_dir + '/' + remote)
			out = open(local, 'wb')
			out.write(f.read())
			out.close()
		except dropbox.rest.ErrorResponse as e:
			#print "Put Error: ", e.error_msg
			return e.status
		return 0

	def delete(self, remote):
		try:
			response = self.drop.file_delete(self.working_dir + '/' + remote)
		except dropbox.rest.ErrorResponse as e:
			#print "Delete Error: ", e.error_msg
			#print "\tStatus: ", e.status
			#print "\tReason: ", e.reason
			#print "\tuser_error_msg: ", e.user_error_msg
			return e.status
		return 0