from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.file import Storage
import argparse
import json
import os
import sys
import datetime
from GoogleSheet import GoogleSheet
from GoogleDrive import GoogleDrive

class VSPerfReport(object):
    def __init__(self, args):
        self.testsheet =  str(args.sheet[0])
        self.template = "1GNY1zcS-oRM7m5zOK-TUewX_0WjWb529DHTUVuxfPLg"
        self.titles = ['Perf']
        self.gsheet = GoogleSheet(self.template, self.titles, "Nightly Test Report")

        self.date = [datetime.datetime.now().strftime('%Y-%m-%d')]
        self.sheet_link = ['https://docs.google.com/spreadsheets/d/' + self.template]

        self.data_64 = []
        self.data_1500 = []
        self.update_current()
        self.get_from_testsheet()
        self.update_data_to_report()

    def update_current(self):
        current_data_64 = self.gsheet.get_batch_data(self.template, "Perf!C1:P5")
        self.gsheet.update_batch_data_row(self.template, "Perf!D1:Q5", current_data_64["valueRanges"][0]["values"])
        current_data_1500 = self.gsheet.get_batch_data(self.template, "Perf!C8:P12")
        self.gsheet.update_batch_data_row(self.template, "Perf!D8:Q12", current_data_1500["valueRanges"][0]["values"])

    def get_from_testsheet(self):
        self.data_64 = self.gsheet.get_row_data(self.testsheet, "Results!B2:D2")
        self.data_1500 = self.gsheet.get_row_data(self.testsheet, "Results!B24:D24")

    def update_data_to_report(self):
        self.gsheet.update_columns(self.template, self.date , "Perf!C1")
        self.gsheet.update_batch_data_col(self.template, "Perf!C3:C5", self.data_64)
        self.gsheet.update_batch_data_col(self.template, "Perf!C8:C10", self.data_1500)
        self.gsheet.update_columns_raw(self.template, self.sheet_link, "Perf!C12")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OVS OFFLOAD Results to Google sheets')
    parser.add_argument('--sheet', nargs=1, type=str, help='Test Result Sheet', required=True)

    args = parser.parse_args()
    nightly_report_sheet = VSPerfReport(args)
