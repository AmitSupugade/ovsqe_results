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

class FlowInsertion(object):
    def __init__(self, args):
        self.ovs = str(args.ovs[0])
        self.data_list=args.data
        self.template = "1EVa_FmwveDiPtKCeg4TzmbYHcsqhGG42CciskrLIMeg"
        self.titles = ['OVS_No_Traffic', 'VFLAG_No_Traffic', 'OVS_with_Traffic', 'VFLAG_with_Traffic']
        self.gsheet = GoogleSheet(self.template, self.titles, "Flow Insertion Rate Test Report")
        self.current_update()
        self.upload_data()

    def upload_data(self):
        i = 0
        data_len = len(self.data_list)
        while i < data_len:
            title = self.titles[i//2]
            cell_10 = title + "!L3"
            cell_100 = title + "!L4"
            self.gsheet.update_columns(self.template, [self.data_list[i]], cell_10)
            i += 1
            self.gsheet.update_columns(self.template, [self.data_list[i]], cell_100)
            i += 1

    def current_update(self):
        for title in self.titles:
            origin = title + "!D3:L6"
            dest = title + "!C3:K6"
            ovs_cell = title + "!L6"
            current_data = self.gsheet.get_batch_data(self.template, origin)
            self.gsheet.update_batch_data_row(self.template, dest, current_data["valueRanges"][0]["values"])
            self.gsheet.update_columns(self.template, [self.ovs], ovs_cell)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Flow Insertion Results to Google sheets')
    parser.add_argument('--ovs', nargs=1, type=str, help='OVS Version', required=True)
    parser.add_argument('--data', nargs='+', type=str, help='List of result data', required=True)

    args = parser.parse_args()
    flow_insertion_result_sheet = FlowInsertion(args)
