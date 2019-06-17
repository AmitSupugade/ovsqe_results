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

class TcPolicyResult(object):
    def __init__(self, args):
        self.result = args.result[0]
        self.topo = str(args.topo[0])
        self.driver = str(args.driver[0])
        self.ovs = str(args.ovs[0])
        self.data_list = [args.data[11 * i:11 * (i + 1)] for i in range(int(len(args.data) / 11))]

        #Template for per driver result upload
        #self.template = "1rDR9ozngEWZzFV9OYAG3VVmDEzFRb1Hrk14VmW9btE0"
        #self.titles = ['Versions and Setup data', 'Topologies', 'Offload Disabled', 'Offload Enabled']

        #Template for combined result upload
        self.template = "1lxiw0oSY08iWIRqWnxJ7rXFY6bOdvRGUXaFPxnDa8wM"
        self.titles = ['Versions_and_Setup_data', 'Topologies', 'skip_hw_Mellanox_Offload_Disabled', 'skip_sw_Mellanox_Offload_Disabled', 'skip_hw_Mellanox_Offload_Enabled', 'skip_sw_Mellanox_Offload_Enabled', 'skip_hw_Netronome_Offload_Disabled', 'skip_sw_Netronome_Offload_Disabled', 'skip_hw_Netronome_Offload_Enabled', 'skip_sw_Netronome_Offload_Enabled']
        self.folder = "109uHIZ7dpNcBfxx8UuZbvwqo3AqtmxGx"

        self.gsheet = GoogleSheet(self.template, self.titles, self.result, self.folder)
        testcell = self.get_test_cell(self.driver, self.topo)

        self.resultsheetId = self.gsheet.get_resultsheet(testcell, self.result)

        self.update_tcpolicy_offload_resultsheet(self.resultsheetId, self.driver, self.topo, self.ovs, self.data_list)


    #Update results in Resultsheet
    def update_tcpolicy_offload_resultsheet(self, spreadsheetId, driver, topo, ovs, data_list):
        self.update_ovs_version(spreadsheetId, ovs)

        for data in data_list:
            frame = int(data[0])
            flows = int(data[1])
            enabled_throughput = [data[2]]
            enabled_latency = [data[4], data[5], data[3]]
            disabled_throughput = [data[6]]
            disabled_latency = [data[8], data[9], data[7]]
            tc_policy=data[10]

            sheets_to_use = self.get_sheets_to_use(tc_policy, driver)
            throughput_range = self.get_throughput_cell(topo, frame, flows)
            latency_range = self.get_latency_cell(topo, frame, flows)

            enabled_throughput_range = sheets_to_use[0] + "!" + throughput_range
            self.update_throughput(spreadsheetId, enabled_throughput, enabled_throughput_range)

            enabled_latency_range = sheets_to_use[0] + "!"  + latency_range
            self.update_latency(spreadsheetId, enabled_latency, enabled_latency_range)

            disabled_throughput_range = sheets_to_use[1] + "!"  + throughput_range
            self.update_throughput(spreadsheetId, disabled_throughput, disabled_throughput_range)

            disabled_latency_range = sheets_to_use[1] + "!"  + latency_range
            self.update_latency(spreadsheetId, disabled_latency, disabled_latency_range)

        print("Results updated to google sheet: {}".format(self.gsheet.get_sheet_link(spreadsheetId)))


    #Update throughput in Result sheet
    def update_throughput(self, spreadsheetId, data, range_name):
        self.gsheet.update_columns(spreadsheetId, data, range_name)


    #Update Latency in Result sheet
    def update_latency(self, spreadsheetId, data, range_name):
        self.gsheet.update_columns(spreadsheetId, data, range_name)


    #Update OVS Version in Result sheet
    def update_ovs_version(self, spreadsheetId, ovs_version):
        data = [ovs_version]
        self.gsheet.update_columns(spreadsheetId, data, "Versions_and_Setup_data!A2")


    def get_test_cell(self, driver, topo):
        if driver =="nfp":
            if topo == "1pf2vf":
                return "skip_hw_Netronome_Offload_Enabled!B3"
            elif topo == "1pf1vf":
                return "skip_hw_Netronome_Offload_Enabled!B27"
            else:
                return ''
        elif driver == "mlx5_core":
            if topo == "1pf2vf":
                return "skip_hw_Mellanox_Offload_Enabled!B3"
            elif topo == "1pf1vf":
                return "skip_hw_Mellanox_Offload_Enabled!B27"
            else:
                return ''
        else:
            return ''


    def get_resultsheet_titles(self, driver):
        if driver == "nfp":
            titles = [ "skip_hw_Netronome_Offload_Enabled", "skip_sw_Netronome_Offload_Enabled", "skip_hw_Netronome_Offload_Disabled", "skip_sw_Netronome_Offload_Disabled" ]
        elif driver == "mlx5_core":
            titles = [ "skip_hw_Mellanox_Offload_Enabled", "skip_sw_Mellanox_Offload_Enabled", "skip_hw_Mellanox_Offload_Disabled", "skip_sw_Mellanox_Offload_Disabled" ]
        else:
            titles = ["Offload_Enabled", "Offload_Disabled"]
        return titles


    def get_sheets_to_use(self, policy, driver):
        list_sheets_to_use = self.get_resultsheet_titles(driver)
        if policy == "skip_hw":
            sheets_to_use = [ list_sheets_to_use[0], list_sheets_to_use[2] ]
        elif policy == "skip_sw":
            sheets_to_use = [ list_sheets_to_use[1], list_sheets_to_use[3] ]
        else:
            sheets_to_use = []
        return sheets_to_use
            


    #Get Latency range
    def get_latency_cell(self, topo, frame, flows):
        if (topo == "1pf2vf"):
            if (frame == 64 and flows == 1):
                return "I2:I4"
            elif (frame == 64 and flows == 10):
                return "J2:J4"
            elif (frame == 64 and flows == 100):
                return "K2:K4"
            if (frame == 1500 and flows == 1):
                return "W2:W4"
            elif (frame == 1500 and flows == 10):
                return "X2:X4"
            elif (frame == 1500 and flows == 100):
                return "Y2:Y4"
            else:
                return -1
        elif (topo == "1pf1vf"):
            if (frame == 64 and flows == 1):
                return "I26:I28"
            elif (frame == 64 and flows == 10):
                return "J26:J28"
            elif (frame == 64 and flows == 100):
                return "K26:K28"
            if (frame == 1500 and flows == 1):
                return "W26:W28"
            elif (frame == 1500 and flows == 10):
                return "X26:X28"
            elif (frame == 1500 and flows == 100):
                return "Y26:Y28"
            else:
                return -1
        else:
            return -1


    #Get throughput range
    def get_throughput_cell(self, topo, frame, flows):
        if(topo == "1pf2vf"):
            if(frame == 64 and flows == 1):
                return "B3"
            elif(frame == 64 and flows == 10):
                return "C3"
            elif(frame == 64 and flows == 100):
                return "D3"
            if(frame == 1500 and flows == 1):
                return "P3"
            elif(frame == 1500 and flows == 10):
                return "Q3"
            elif(frame == 1500 and flows == 100):
                return "R3"
            else:
                return -1
        elif(topo == "1pf1vf"):
            if(frame == 64 and flows == 1):
                return "B27"
            elif(frame == 64 and flows == 10):
                return "C27"
            elif(frame == 64 and flows == 100):
                return "D27"
            if (frame == 1500 and flows == 1):
                return "P27"
            elif (frame == 1500 and flows == 10):
                return "Q27"
            elif (frame == 1500 and flows == 100):
                return "R27"
            else:
                return -1
        else:
            return -1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OVS OFFLOAD Results to Google sheets')
    parser.add_argument('--result', nargs=1, type=str, help='Name of the result sheet', required=True)
    parser.add_argument('--ovs', nargs=1, type=str, help='OVS Version', required=True)
    parser.add_argument('--driver', nargs=1, type=str, help='NIC Driver. Ex: npf, mlx5_core', required=True)
    parser.add_argument('--topo', nargs=1, type=str, help='Test Topology. Available options: 1pf2vf, 1pf1vf', required=True)
    parser.add_argument('--data', nargs='+', type=str, help='List of result data', required=True)

    args = parser.parse_args()
    TcPolicy_result_sheet = TcPolicyResult(args)
