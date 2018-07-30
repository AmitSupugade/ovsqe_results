from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.file import Storage
import argparse
import json
import os
import sys


class GoogleSheet(object):
    def __init__(self, template_id, result_title, titles):
        self.template_id = template_id
        self.result_title = result_title
        self.titles = titles

        self.result = None
        self.result_sheetId = None
        self.service = self.get_service()
        self.sheet_list = self.get_sheets(self.template_id)

        #self.create_result_sheet()


    def get_resultsheet(self):
        return self.result


    def get_resultId(self):
        return self.result_sheetId


    #Create credentials to access Googlesheets
    def get_credentials(self):
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
    def get_service(self):
        creds = self.get_credentials()
        service = build('sheets', 'v4', http=creds.authorize(Http()))
        return service


    #Returns Id of a Spreadsheet
    def get_spreadsheet_id(self, s):
        return s['spreadsheetId']


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


    #Create Result Sheet
    def create_result_sheet(self):
        self.create_sheet(self.result_title)
        self.make_copy(self.template_id, self.result_sheetId)
        self.update_titles()
        print("Link to Result Sheet: {}".format(self.get_sheet_link(self.result_sheetId)))
        return self.result
        #return self.result_sheetId


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
        print("New Sheet Created!")
        self.result = sheet
        self.result_sheetId = self.get_spreadsheet_id(self.result)


    #Copy One Spreadsheet to another
    def make_copy(self, sourceId, destinationId):
        spreadsheet_body = {
            'destination_spreadsheet_id' : destinationId,
        }

        for sheet in self.sheet_list:
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





"""

def main():
    template_id = "1rDR9ozngEWZzFV9OYAG3VVmDEzFRb1Hrk14VmW9btE0"
    sheet_titles = ['Versions and Setup data','Topologies','Offload Disabled','Offload Enabled']
    result_sheet_title = "New_result"
    sheet = GoogleSheet(template_id, sheet_titles)
    sheet.create_result_sheet(result_sheet_title)
    #result_sheet = sheet.create_sheet(result_sheet_title)
    #result_sheet_id = result_sheet['spreadsheetId']
    #sheet.make_copy(template_id, result_sheet_id)
    #sheet.update_titles()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OVSQE Results to Google sheets')
    parser.add_argument('--template', nargs=1, type=str, help='ID of a result sheet template', required=True)
    parser.add_argument('--result', nargs=1, type=str, help='Name of the result sheet', required=True)
    parser.add_argument('--titles', nargs='+', type=str, help='List of sheet titles in result spreadsheet', required=True)

    args = parser.parse_args()
    SHEETS = GoogleSheet(args)

"""