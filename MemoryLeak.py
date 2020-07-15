from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.file import Storage
import argparse
import json
import os
import sys
import urllib.request
from GoogleSheet import GoogleSheet
from GoogleDrive import GoogleDrive


class MemoryLeak(object):
    def __init__(self, args):
        self.resultsheetName = str(args.name[0])

        self.template = "18XIVzlMeffUsw_ai4BfWlNsfhKVJ4_Tp9hvMKHAhjek"
        self.titles = ['64B 1K Flows', '256B 5K Flows', '512B 10K Flows', '1500B 25K Flows', '2000B 100K Flowss', '9000B 1M Flows']
        self.folder = "1z97pwJ03gWCwKbsZdxBGLybvvpEy4CGa"
        self.files = ['memory_pvp_kernel_64bytes_1kflows.txt', 'memory_pvp_kernel_256bytes_5kflows.txt', 'memory_pvp_kernel_512bytes_10kflows.txt', 'memory_pvp_kernel_1500bytes_25kflows.txt', 'memory_pvp_kernel_2000bytes_100kflows.txt', 'memory_pvp_kernel_9000bytes_1mflows.txt']

        self.gsheet = GoogleSheet(self.template, self.titles, self.resultsheetName, self.folder)
        self.resultsheetId = self.gsheet.get_resultsheet("A3", self.resultsheetName)

        self.kb_in_use = []
        self.kb_lost = []
        self.percentage_lost = []


        for i in range(len(self.files)):
            filename = self.files[i]
            title = self.titles[i]
            self.readTxt(filename)
            self.update_resultsheet(title)
            print("Updated from file: ", filename)
            
        print("Done")
        print("Report Sheet Link- https://docs.google.com/spreadsheets/d/"+self.resultsheetId)


    def update_resultsheet(self, title):
        self.gsheet.update_columns(self.resultsheetId, self.kb_in_use, title + "!A6:A29")
        self.gsheet.update_columns(self.resultsheetId, self.kb_lost, title + "!B6:B29")
        self.gsheet.update_columns(self.resultsheetId, self.percentage_lost, title + "!C6:C29")


    def readTxt(self, filename):
        kb_in_use = []
        kb_lost = []
        percentage_lost = []

        file = f = open(filename, "r")
        for line in file:
            line_data = line.split()
            kb_in_use.append(line_data[5])
            kb_lost.append(line_data[7])
            percentage_lost.append(line_data[9])

        self.kb_in_use = kb_in_use[2:]
        self.kb_lost = kb_lost[2:]
        self.percentage_lost = percentage_lost[2:]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Memory Leak test results to Google sheets')
    parser.add_argument('--name', nargs=1, type=str, help='Result Sheet Name', required=True)

    args = parser.parse_args()
    memory_leak_report_sheet = MemoryLeak(args)
