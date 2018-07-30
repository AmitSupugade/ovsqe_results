from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.file import Storage
import argparse
import json
import os
import sys

class GoogleDrive(object):

    def __init__(self):
        self.service = self.get_drive_service()

   #Create credentials to access Google drive
    def get_drive_credentials(self):
        SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'ovs-offload-results'

        store = file.Storage('token.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)

        return creds

    #Create a service to access Google drive
    def get_drive_service(self):
        creds = self.get_drive_credentials()
        service = build('drive', 'v3', http=creds.authorize(Http()))
        return service


    def search_spreadsheet_by_title(self, title):
        results = self.service.files().list(q="name contains '" + title + "' and mimeType = 'application/vnd.google-apps.spreadsheet'").execute()
        items = results.get('files', [])
        if len(items) == 1:
            return items[0]['id']
        return ''
