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

        self.template = "1GH8_N4zmQ1WNdJOUcIYaQOKUOv8kNw8HzP2vXg_aw18"
        self.titles = ['Kernel 64B 1K Flows', 'Kernel 256B 5K Flows', 'Kernel 512B 10K Flows', 'Kernel 1500B 25K Flows', 'Kernel 2000B 100K Flows', 'Kernel 9000B 1M Flows', 'DPDK 64B 1K Flows', 'DPDK 256B 5K Flows', 'DPDK 512B 10K Flows', 'DPDK 1500B 25K Flows', 'DPDK 2000B 100K Flowss', 'DPDK 9000B 1M Flows']
        self.folder = "1z97pwJ03gWCwKbsZdxBGLybvvpEy4CGa"
        self.files = ['memory_pvp_kernel_64bytes_1kflows.txt', 'memory_pvp_kernel_256bytes_5kflows.txt', 'memory_pvp_kernel_512bytes_10kflows.txt', 'memory_pvp_kernel_1500bytes_25kflows.txt', 'memory_pvp_kernel_2000bytes_100kflows.txt', 'memory_pvp_kernel_9000bytes_1mflows.txt', 'memory_pvp_dpdk_64bytes_1kflows.txt', 'memory_pvp_dpdk_256bytes_5kflows.txt', 'memory_pvp_dpdk_512bytes_10kflows.txt', 'memory_pvp_dpdk_1500bytes_25kflows.txt', 'memory_pvp_dpdk_2000bytes_100kflows.txt', 'memory_pvp_dpdk_9000bytes_1mflows.txt']

        self.gsheet = GoogleSheet(self.template, self.titles, self.resultsheetName, self.folder)
        self.resultsheetId = self.gsheet.get_resultsheet("A3", self.resultsheetName)

        self.kb_in_use = []
        self.kb_lost = []
        self.percentage_lost = []

        for i in range(len(self.files)):
            filename = "/mnt/tests/kernel/networking/openvswitch/memory_leak_soak/" + self.files[i]
            if os.path.isfile(filename):
                title = self.titles[i]
                res = self.readTxt(filename)
                self.update_resultsheet(title, res)
                print("Updated from file: ", filename)
            else:
                print(filename + " does not exist.")
        print("Done")
        print("Report Sheet Link- https://docs.google.com/spreadsheets/d/"+self.resultsheetId)


    def update_resultsheet(self, title, res):
        self.gsheet.update_columns(self.resultsheetId, [res[0]], title + "!B1")
        self.gsheet.update_columns(self.resultsheetId, [res[1]], title + "!B2")
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
        pid = line_data[1]
        interval = line_data[3]
        result = (pid, interval)

        self.kb_in_use = kb_in_use[2:]
        self.kb_lost = kb_lost[2:]
        self.percentage_lost = percentage_lost[2:]
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Memory Leak test results to Google sheets')
    parser.add_argument('--name', nargs=1, type=str, help='Result Sheet Name', required=True)

    args = parser.parse_args()
    memory_leak_report_sheet = MemoryLeak(args)
