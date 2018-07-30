from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.file import Storage
import argparse
import json
import os
import sys
from GoogleDrive import GoogleDrive


class GoogleSheet(object):
    def __init__(self, template_id, result_title, titles):
        self.template_id = template_id
        self.result_title = result_title
        self.titles = titles

        self.result_sheetId = None
        self.service = self.get_sheet_service()
        self.drive = GoogleDrive()


    #Returns ID of result spreadsheet
    def get_resultsheetId(self):
        return self.result_sheetId


    #Create credentials to access Googlesheets
    def get_sheet_credentials(self):
        SCOPES = 'https://www.googleapis.com/auth/drive'
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'ovs-offload-results'

        store = file.Storage('token.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)

        return creds


    #Create a service to access Googlesheets
    def get_sheet_service(self):
        creds = self.get_sheet_credentials()
        service = build('sheets', 'v4', http=creds.authorize(Http()))
        return service


    #Returns Id of a Spreadsheet
    def get_spreadsheet_id(self, spreadsheet):
        return spreadsheet['spreadsheetId']


    #Returns Spreadsheet from Id
    def get_spreadsheet(self, id):
        return self.service.spreadsheets().get(spreadsheetId=id).execute()


    #Returns Ids of all sheets in a Spreadsheet
    def get_sheets(self, id):
        sheets = []
        spreadsheet = self.get_spreadsheet(id)

        for sheet in spreadsheet.get("sheets", None):
            sheets.append(sheet['properties']['sheetId'])

        return sheets


    def get_resultsheet(self):
        present =  self.drive.search_spreadsheet_by_title(self.result_title)
        if not present:
            self.create_result_sheet()
        else:
            self.result_sheetId = present
        return self.result_sheetId


    #Create Result Sheet
    def create_result_sheet(self):
        self.create_sheet(self.result_title)
        self.make_copy(self.template_id, self.result_sheetId)
        self.update_titles()
        return self.result_sheetId


    #Returns Google drive link of result sheet
    def get_sheet_link(self, sheetId):
        return "https://docs.google.com/spreadsheets/d/{}".format(sheetId)


    #Create a New Empty Spreadsheet
    def create_sheet(self, title):
        spreadsheet_body = {
          "properties" : {
            "title" : title,
            "locale" : 'en',
            "autoRecalc": 'ON_CHANGE'
          },
        }

        sheet =  self.service.spreadsheets().create(body = spreadsheet_body).execute()
        self.result_sheetId = self.get_spreadsheet_id(sheet)


    #Copy One Spreadsheet to another
    def make_copy(self, sourceId, destinationId):
        spreadsheet_body = {
            'destination_spreadsheet_id' : destinationId,
        }

        sheet_list = self.get_sheets(self.template_id)
        for sheet in sheet_list:
            new_sheet = self.service.spreadsheets().sheets().copyTo(spreadsheetId=sourceId,
                                               body=spreadsheet_body, sheetId=sheet).execute()

        result_sheets = self.get_sheets(self.result_sheetId)

        if len(result_sheets) > 1:
            self.delete_sheet(self.result_sheetId, result_sheets[0])


    #Update titles of sheets
    def update_titles(self):
        result_sheets = self.get_sheets(self.result_sheetId)

        for i in range(len(self.titles)):
            title = self.titles[i]
            sheetId = result_sheets[i]
            sheet_body = {
                "requests" : [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId" : sheetId,
                                "title" : title
                            },
                            "fields": 'title'
                        }
                    }
                ]
            }

            self.service.spreadsheets().batchUpdate(spreadsheetId=self.result_sheetId,
                                                    body=sheet_body).execute()


    #Delete Single sheet from Spreadsheet
    def delete_sheet(self, spreadsheetId, sheetId):
        sheet_body = {
            "requests": [
                {
                    "deleteSheet": {
                        "sheetId": str(sheetId)
                    }
                }
            ]
        }

        self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId,
                                                body=sheet_body).execute()


    #Add data column-wise
    def update_columns(self, spreadsheetId, data, range_name):
        body = {
            'majorDimension': "COLUMNS",
            'values': [
                data
            ]
        }

        return self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheetId, range=range_name,
            valueInputOption="USER_ENTERED", body=body).execute()


    #Add data row-wise
    def update_rows(self, spreadsheetId, data, range_name):
        body = {
            'majorDimension': "ROWS",
            'values': [
                data
            ]
        }

        return self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheetId, range=range_name,
            valueInputOption="USER_ENTERED", body=body).execute()

