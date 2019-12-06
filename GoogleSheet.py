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
    def __init__(self, template_id, titles, title, folder=''):
        self.template_id = template_id
        self.titles = titles
        self.folder = folder
        self.title = title

        self.result_sheetId = None
        self.service = self.get_sheet_service()
        self.drive = GoogleDrive()
        self.count = 0


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


    #Returns ID of result spreadsheet
    def get_resultsheetId(self):
        return self.result_sheetId


    # Returns Google drive link of result sheet
    def get_sheet_link(self, sheetId):
        return "https://docs.google.com/spreadsheets/d/{}".format(sheetId)


    #Returns Spreadsheet from Id
    def get_spreadsheet(self, id):
        return self.service.spreadsheets().get(spreadsheetId=id).execute()


    #Returns Id of a Spreadsheet
    def get_spreadsheet_id(self, spreadsheet):
        return spreadsheet['spreadsheetId']


    #Returns Ids of all sheets in a Spreadsheet
    def get_sheets(self, id):
        sheets = []
        spreadsheet = self.get_spreadsheet(id)

        for sheet in spreadsheet.get("sheets", None):
            sheets.append(sheet['properties']['sheetId'])

        return sheets


    #Search for given sheet title, if doesnt exist create new sheet
    def get_resultsheet(self, testcell, new_title):
        present =  self.drive.search_spreadsheet_by_title(new_title, self.folder)
        if not present:
            #print("Sheet not present")
            self.result_sheetId = self.create_result_sheet(new_title)
        else:
            if not self.check_testcell(present, testcell):
                #print("Cell Empty")
                self.result_sheetId = present
            else:
                #print("Cell not Empty")
                self.count += 1
                new_title = self.title + "_" + str(self.count)
                self.result_sheetId = self.get_resultsheet(testcell, new_title)
        self.count = 0
        return self.result_sheetId


    #Returns False if cell is Empty
    def check_testcell(self, spreadsheetId, testcell):
        celldata = self.service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=testcell).execute()
        if len(celldata) == 3:
            return True
        return False


    #Create Result Sheet
    def create_result_sheet(self, title):
        resultsheetId = self.create_new_sheet(title, self.folder)
        self.make_copy(self.template_id, resultsheetId)
        self.update_titles(resultsheetId)
        return resultsheetId


    #Create new empty sheet
    def create_new_sheet(self, title, folder):
        if not folder:
            resultsheetId = self.create_sheet(title)
        else:
            resultsheetId = self.create_sheet_in_folder(title, folder)
        return resultsheetId


    #Create Empty Spreadsheet
    def create_sheet(self, title):
        spreadsheet_body = {
          "properties" : {
            "title" : title,
            "locale" : 'en',
            "autoRecalc": 'ON_CHANGE'
          },
        }

        sheet =  self.service.spreadsheets().create(body = spreadsheet_body).execute()
        return self.get_spreadsheet_id(sheet)


    #Create a New Empty Spreadsheet in given folder
    def create_sheet_in_folder(self, title, folder):
        return self.drive.create_result_sheet(title, folder)


    #Copy One Spreadsheet to another
    def make_copy(self, sourceId, destinationId):
        spreadsheet_body = {
            'destination_spreadsheet_id' : destinationId,
        }

        sheet_list = self.get_sheets(self.template_id)

        for sheet in sheet_list:
            new_sheet = self.service.spreadsheets().sheets().copyTo(spreadsheetId=sourceId,
                                               body=spreadsheet_body, sheetId=sheet).execute()

        result_sheets = self.get_sheets(destinationId)

        if len(result_sheets) > 1:
            self.delete_sheet(destinationId, result_sheets[0])


    #Update titles of sheets
    def update_titles(self, resultsheetId):
        result_sheets = self.get_sheets(resultsheetId)

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

            self.service.spreadsheets().batchUpdate(spreadsheetId=resultsheetId,
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


    #Get Data from cells row-wise
    def get_row_data(self, spreadsheetId, range_name):
        return self.service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
	    range=range_name, majorDimension="ROWS").execute()['values']


    #Get Data from cells column-wise
    def get_column_data(self, spreadsheetId, range_name):
        return self.service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
	    range=range_name, majorDimension="COLUMNS").execute()['values']


    #Get Batch Data
    def get_batch_data(self, spreadsheetId, ranges):
        return self.service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
	    ranges=ranges, majorDimension="ROWS").execute()

    #Update Batch Data
    def update_batch_data(self, spreadsheetId, range, data):
        body = {
            "valueInputOption": "RAW",
            "includeValuesInResponse": False,
            "data": [{
            'range': range,
            'majorDimension': "ROWS",
            'values': data }]
        }
        return self.service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId,
	    body=body).execute()


"""
    #Search for given sheet title, if doesnt exist create new sheet
    def get_resultsheet(self, testcell, title):
        present =  self.drive.search_spreadsheet_by_title(title)
        if not present:
            self.create_result_sheet(title)
        else:
            self.result_sheetId = present
        return self.result_sheetId

"""

"""
S = GoogleSheet("1hBBDQCCcI9HWoJeVWeMlKKxMjzCmOCOMd84f55snuXE", ["Sheet1"], "Sheet1")
results = S.get_batch_data("1hBBDQCCcI9HWoJeVWeMlKKxMjzCmOCOMd84f55snuXE", ["D6:M7"])
data = results["valueRanges"][0]["values"]
print(data)
mydata=[{"range":"C6:L7", "values":data, "majorDimension": "ROWS"}]
mybody = { "valueInputOption":"RAW", "includeValuesInResponse": False, "data":mydata}
S.update_batch_data("1hBBDQCCcI9HWoJeVWeMlKKxMjzCmOCOMd84f55snuXE", "B9:K10", data)
"""
