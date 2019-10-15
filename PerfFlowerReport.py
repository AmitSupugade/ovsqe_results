from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.file import Storage
import argparse
import json
import os
import sys
from GoogleSheet import GoogleSheet
from GoogleDrive import GoogleDrive

class PerfFlowerReport(object):
    def __init__(self, args):
        self.dataset_20k = [args.data20k[3 * i:3 * (i + 1)] for i in range(int(len(args.data20k) / 3))]
        self.dataset_40k = [args.data40k[3 * i:3 * (i + 1)] for i in range(int(len(args.data40k) / 3))]
        self.template = "1PzDCMA65z4J597PXEb3wMQ-e-RxYQhJ2_cGKiyzON1s"
        self.titles = ['Report']
        self.gsheet = GoogleSheet(self.template, self.titles, "Flow Insertion Rate Test Report")
	self.cells=['K', 'J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B']

        self.upload_data()

    def upload_data(self):
        for i in range(len(self.dataset_20k)):
            column = self.cells[i]
            range_20k = 'Report!' + column + '3:' + column + '6'
            data_20k = self.dataset_20k[i]
            self.gsheet.update_columns(self.template, data_20k, range_20k)

            range_40k = 'Report!' + column + '9:' + column + '12'
            data_40k = self.dataset_40k[i]
            self.gsheet.update_columns(self.template, data_40k, range_40k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OVS OFFLOAD Results to Google sheets')
    parser.add_argument('--data20k', nargs='+', type=str, help='List of result data for 20K flows', required=True)
    parser.add_argument('--data40k', nargs='+', type=str, help='List of result data for 40K flows', required=True)

    args = parser.parse_args()
    perf_flower_report_sheet = PerfFlowerReport(args)
