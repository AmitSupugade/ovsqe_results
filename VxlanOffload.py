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

class VxlanOffload(object):
    def __init__(self, args):
        self.ovs = str(args.ovs[0])
        self.data = str(args.data[0])
        print(self.ovs, self.data)
        self.template = "1pI_ewDbLbriKqXORkaalCmgsxZpm1lJWRv3g92Wltx4"
        self.titles = ['VxLAN Offload']
        self.gsheet = GoogleSheet(self.template, self.titles, "VxLAN Offload Test Report")
        self.current_update()
        self.upload_data()
        print("Data Uploaded Successfully.")

    def upload_data(self):
        cell = self.titles[0] + "!L3"
        self.gsheet.update_columns(self.template, [self.data], cell)

    def current_update(self):
        origin = self.titles[0] + "!D3:L5"
        dest = self.titles[0] + "!C3:K5"
        ovs_cell = self.titles[0] + "!L5"
        current_data = self.gsheet.get_batch_data(self.template, origin)
        self.gsheet.update_batch_data_row(self.template, dest, current_data["valueRanges"][0]["values"])
        self.gsheet.update_columns(self.template, [self.ovs], ovs_cell)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VxLAN Offload Test Results to Google sheets')
    parser.add_argument('--ovs', nargs=1, type=str, help='OVS Version', required=True)
    parser.add_argument('--data', nargs='+', type=str, help='Test data', required=True)

    args = parser.parse_args()
    vxlan_offload_result_sheet = VxlanOffload(args)
