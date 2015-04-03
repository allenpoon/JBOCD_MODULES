# Include the Google Drive SDK
import os
import sys
import simplejson
import string
import ConfigParser
import httplib2
import json
import oauth2client.client
from urllib import urlencode
from oauth2client.client import AccessTokenCredentials
from apiclient.discovery import build
from apiclient import errors

def PrintHelp():
    print "Python Google Drive Deleter"
    print "usage: python delete.py [access token] [remote file path]"

if len(sys.argv) < 2 : print "Delete.py: Access token cannot be null. (Argument 1)"
elif len(sys.argv) < 3 : print "Delete.py: Please enter the file you want to delete. (Argument 2)"
else:
    def ConfigSectionMap(section):
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

    # Get configuration file
    Config = ConfigParser.ConfigParser()
    Config.read("/var/JBOCD/module/googledrive/config.ini")
    CLIENT_ID = ConfigSectionMap("googledrive")['clientid']
    CLIENT_SECRET = ConfigSectionMap("googledrive")['clientsecret']
    REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    SCOPES = ['https://www.googleapis.com/auth/drive']

    at = simplejson.loads(sys.argv[1])
    #h = httplib2.Http()
    #d = {"grant_type": "refresh_token", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID, "refresh_token": at['refresh_token']}
    #resp, content = h.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
    
    #credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')
    credstr = '{"_module": "oauth2client.client", "token_expiry": null, "access_token": null, "token_uri": null, "invalid": false, "token_response": null, "client_id": "%s", "id_token": null, "client_secret": "%s", "revoke_uri": null, "_class": "AccessTokenCredentials", "refresh_token": "%s", "user_agent": "python-jbocd/1.0"}' % (  CLIENT_ID, CLIENT_SECRET, at['refresh_token'])
    credentials = AccessTokenCredentials.from_json(credstr)
    http = httplib2.Http()
    try:
        credentials.refresh(http)
    except oauth2client.client.AccessTokenCredentialsError:
        print "Refresh needed!"
        d = {"grant_type": "refresh_token", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID, "refresh_token": at['refresh_token']}
        resp, content = http.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
        credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')

    http = httplib2.Http()
    http = credentials.authorize(http)
    drive = build('drive', 'v2', http=http)

    try:
        root = drive.about().get().execute()['rootFolderId']
        str = sys.argv[2]
        cur = root
        strsplt = str[1:].split('/')
        filename = strsplt[len(strsplt)-1]

        if len(strsplt) > 1:
            for folder in strsplt:
                param = {}
                param['pageToken'] = cur
                childrens = drive.children().list(folderId=cur).execute()
                for item in childrens['items']:
                    sitem = drive.files().get(fileId=item['id']).execute()
                    if sitem["labels"]["trashed"] == False and sitem["mimeType"] == "application/vnd.google-apps.folder":
                        if sitem["title"]==folder:
                            cur = item['id']
                            break

            if drive.files().get(fileId=cur).execute()['title'] != strsplt[len(strsplt)-2]:
                print "Directory not found!"
                exit(2)

        childrens = drive.children().list(folderId=cur).execute()
        for item in childrens['items']:
            sitem = drive.files().get(fileId=item['id']).execute()
            if sitem['title'] == filename:
                drive.files().delete(fileId=sitem['id']).execute()
                drive.files().emptyTrash()
                sys.exit(0)
    except errors.HttpError, e:
        #print 'Error: %s' % e
        try:
            # Load Json body.
            error = simplejson.loads(e.content)
            print 'Error code: %d' % error.get('code')
            print 'Error message: %d' % error.get('message')
            sys.exit(error.get('code'))

            # More error information can be retrieved with error.get('errors').
        except TypeError:
            # Could not load Json body.
            print 'HTTP Status code: %d' % e.resp.status
            print 'HTTP Reason: %s' % e.resp.reason
            sys.exit(e.resp.status)
        except ValueError:
            # Could not load Json body.
            print 'HTTP Status code: %d' % e.resp.status
            print 'HTTP Reason: %s' % e.resp.reason
            sys.exit(e.resp.status)
    
    sys.exit(1)
