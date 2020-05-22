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

class GatingReport(object):
    def __init__(self, args):
        self.testsheet = str(args.sheet[0])
        #self.nic = args.nic[0]

        tsheet = GoogleSheet(self.testsheet)
        self.ovs_rpm = self.get_ovs_rpm(tsheet)
        self.ovs = self.ovs_rpm.split("-")[1]
        self.kernel = self.get_kernel(tsheet)
        self.nic = self.get_nic(tsheet)

        self.template = self.get_template()
        self.titles = ['No_VLAN', 'VLAN', 'Guest_Enable_IOMMU', 'Enable_Mergable_Buffers', 'Higher_Flows', 'Ovs_Kernel_LinuxBridge']
        self.gsheet = GoogleSheet(self.template)

        template_title = self.gsheet.get_spreadsheet(self.template)['properties']['title']
        print("Title of Report sheet- ", template_title)
        template_link = self.gsheet.get_sheet_link(self.template)
        print("Link of Report sheet- ", template_link)

        self.update_current()
        self.update_no_vlan()
        self.update_vlan()
        self.update_guest_enable_iommu()
        self.update_enable_mergable_buffers()
        self.update_higher_flows()
        self.update_ovs_kernel_linuxbridge()
        print("Done.")


#Functions to perform sheet updates
    def update_no_vlan(self):
        self.update_64_no_vlan()
        self.update_128_no_vlan()
        self.update_256_no_vlan()
        self.update_1500_no_vlan()
        print("Updated: No_VLAN sheet.")

    def update_vlan(self):
        self.update_64_vlan()
        self.update_128_vlan()
        self.update_256_vlan()
        self.update_1500_vlan()
        print("Updated: VLAN sheet.")

    def update_guest_enable_iommu(self):
        self.update_64_guest_enable_iommu()
        self.update_128_guest_enable_iommu()
        self.update_256_guest_enable_iommu()
        self.update_1500_guest_enable_iommu()
        print("Updated: Guest_Enable_IOMMU sheet.")

    def update_enable_mergable_buffers(self):
        self.update_64_enable_mergable_buffers()
        self.update_1500_enable_mergable_buffers()
        print("Updated: Enable_Mergable_Buffers sheet.")

    def update_higher_flows(self):
        self.update_64_higher_flows()
        self.update_1500_higher_flows()
        print("Updated: Higher_Flows sheet.")

    def update_ovs_kernel_linuxbridge(self):
        self.update_64_ovs_kernel_linuxbridge()
        self.update_1500_ovs_kernel_linuxbridge()
        print("Updated: Ovs_Kernel_LinuxBridge sheet.")


#Functions to update ovs_kernel_linuxBridge sheet
    def update_64_ovs_kernel_linuxbridge(self):
        cells = ["M3", "M4"]
        data = self.gsheet.get_row_data(self.testsheet, "OVS-Kernel-Linuxbridge!B2:C2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "OVS_Kernel_LinuxBridge!" + cells[i])

    def update_1500_ovs_kernel_linuxbridge(self):
        cells = ["M5", "M6"]
        data = self.gsheet.get_row_data(self.testsheet, "OVS-Kernel-Linuxbridge!B2:C2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "OVS_Kernel_LinuxBridge!" + cells[i])

#Functions to update Higher Flows sheet
    def update_64_higher_flows(self):
        cells = ["M3", "M4", "M5"]
        data = self.gsheet.get_row_data(self.testsheet, "64 Bytes Higher Flow!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "Higher_Flows!" + cells[i])

    def update_1500_higher_flows(self):
        cells = ["M6", "M7", "M8"]
        data = self.gsheet.get_row_data(self.testsheet, "1500 Bytes Higher Flow!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "Higher_Flows!" + cells[i])


#Functions to update Enable_Mergable_Buffers sheet
    def update_64_enable_mergable_buffers(self):
        cells = ["M3", "M4"]
        data = self.gsheet.get_row_data(self.testsheet, "64 Bytes Enable Mergable Buffers!B2:C2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "Enable_Mergable_Buffers!" + cells[i])

    def update_1500_enable_mergable_buffers(self):
        cells = ["M5", "M6"]
        data = self.gsheet.get_row_data(self.testsheet, "1500 Bytes Enable Mergable Buffers!B2:C2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "Enable_Mergable_Buffers!" + cells[i])


#Functions to update Guest_Enable_IOMMU sheet
    def update_64_guest_enable_iommu(self):
        cells = ["M2", "M3", "M4"]
        data = self.gsheet.get_row_data(self.testsheet, "64 Bytes Guest Enable Iommu!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "Guest_Enable_IOMMU!" + cells[i])

    def update_128_guest_enable_iommu(self):
        cells = ["M5", "M6", "M7"]
        data = self.gsheet.get_row_data(self.testsheet, "128 Bytes Guest Enable Iommu!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "Guest_Enable_IOMMU!" + cells[i])

    def update_256_guest_enable_iommu(self):
        cells = ["M8", "M9", "M10"]
        data = self.gsheet.get_row_data(self.testsheet, "256 Bytes Guest Enable Iommu!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "Guest_Enable_IOMMU!" + cells[i])

    def update_1500_guest_enable_iommu(self):
        cells = ["M11", "M12", "M13"]
        data = self.gsheet.get_row_data(self.testsheet, "1500 Bytes Guest Enable Iommu!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "Guest_Enable_IOMMU!" + cells[i])


#Functions to update vlan sheet
    def update_64_vlan(self):
        cells = ["M2", "M3", "M4"]
        data = self.gsheet.get_row_data(self.testsheet, "64 Bytes VLAN!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "VLAN!" + cells[i])

    def update_128_vlan(self):
        cells = ["M5", "M6", "M7"]
        data = self.gsheet.get_row_data(self.testsheet, "128 Bytes VLAN!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "VLAN!" + cells[i])

    def update_256_vlan(self):
        cells = ["M8", "M9", "M10"]
        data = self.gsheet.get_row_data(self.testsheet, "256 Bytes VLAN!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "VLAN!" + cells[i])

    def update_1500_vlan(self):
        cells = ["M11", "M12", "M13"]
        data = self.gsheet.get_row_data(self.testsheet, "1500 Bytes VLAN!B2:D2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "VLAN!" + cells[i])


#Functions to update no_vlan sheet
    def update_64_no_vlan(self):
        cells = ["M2", "M3", "M4", "M5", "M6"]
        data = self.gsheet.get_row_data(self.testsheet, "64 Bytes No VLAN!B2:F2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "No_VLAN!"+cells[i])

    def update_128_no_vlan(self):
        cells = ["M7", "M8", "M10", "M11"]
        data = self.gsheet.get_row_data(self.testsheet, "128 Bytes No VLAN!B2:E2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "No_VLAN!"+cells[i])

    def update_256_no_vlan(self):
        cells = ["M12", "M13", "M15", "M16"]
        data = self.gsheet.get_row_data(self.testsheet, "256 Bytes No VLAN!B2:E2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "No_VLAN!"+cells[i])

    def update_1500_no_vlan(self):
        cells = ["M17", "M18", "M19", "M20", "M21"]
        data = self.gsheet.get_row_data(self.testsheet, "1500 Bytes No VLAN!B2:F2")[0]
        for i in range(len(cells)):
            self.gsheet.update_columns(self.template, [data[i]], "No_VLAN!"+cells[i])


#Function to shift existing data and add ovs and kernel info
    def update_current(self):
        range_from = ['E2:M24', 'E2:M16', 'E2:M16', 'E3:M9', 'E3:M11', 'E3:M9']
        range_to = ['D2:L24', 'D2:L16', 'D2:L16', 'D3:L9', 'D3:L11', 'D3:L9']
        cells_ovs = ["M23", "M15", "M15", "M8", "M10", "M8"]
        cells_kernel = ["M24", "M16", "M16", "M9", "M11", "M9"]
        l = len(self.titles)
        for i in range(l):
            origin = self.titles[i] + "!" + range_from[i]
            dest = self.titles[i] + "!" + range_to[i]
            ovs_cell = self.titles[i] + "!" + cells_ovs[i]
            kernel_cell = self.titles[i] + "!" + cells_kernel[i]
            current_data = self.gsheet.get_batch_data(self.template, origin)
            self.gsheet.update_batch_data_row(self.template, dest, current_data["valueRanges"][0]["values"])
            self.gsheet.update_columns(self.template, [self.ovs_rpm], ovs_cell)
            self.gsheet.update_columns(self.template, [self.kernel], kernel_cell)
        print("Updated: Existing data.")
        print("Updated: ovs and kernel info.")


#Helper Functions
    def get_ovs_rpm(self, tsheet):
        cell_data = tsheet.get_row_data(self.testsheet, "Version and Setup data!A2")[0][0].split("\n")
        ovs_rpm = [data for data in cell_data if "openvswitch2" in data][0]
        print("OVS_rpm= ", ovs_rpm)
        return ovs_rpm

    def get_kernel(self, tsheet):
        kernel = tsheet.get_row_data(self.testsheet, "Version and Setup data!A20")[0][0].split(":")[1]
        print("Kernel= ", kernel)
        return kernel

    def get_nic(self, tsheet):
        nic = tsheet.get_spreadsheet(self.testsheet)['properties']['title'].split("_")[0]
        print("NIC= ", nic)
        return nic

    def get_template(self):
        #NICs=ixgbe, i40e, QLogic QEDE, Broadcom bnxt, Mellanox CX-5, Netronome
        rhel = self.kernel.split('el')[1][0]
        ovs_version = self.ovs.split('.')[1]
        if self.nic == "mlx5":
            if rhel == "7":
                if ovs_version == "11":
                    return "1d93790mANlkN-Y_Z4gawJNhpSh-mrsLaajpLisxVgqE"
                elif ovs_version == "12":
                    return "1pg-SeSXRRrU9kAqW7avRnRGBejPuLG5P1tVi19wPiuQ"
                elif ovs_version == "13":
                    return "1GIgZfxhUe2nx9vBFzJtNJme_JHxG7-CxXQTupu8n2zg"
            elif rhel == "8":
                if ovs_version == "11":
                    return "1QKOA9bK_Ur7fImQ_o5SpOnBVCsEZ4NfkKh8ivyyQJn0"
                elif ovs_version == "12":
                    return "1j3GupuGnOOe_iQlzqtZgWMEN22fkFBt6ry8OlnWjWAk"
                elif ovs_version == "13":
                    return "1yXl2KVwB5FxbqfCw9dtBO06adzFkRtYfY0qvm3tHjB8"
        elif self.nic == "nfp":
            if rhel == "7":
                if ovs_version == "11":
                    return "1d6qdUueFh_cZIrpbxH8w3z2MbjUZR_Vkj0eC_RPjmsE"
                elif ovs_version == "12":
                    return "1fbcxUUCSoCmQTUzJPQc7IEjDdEU56jPiXalxOt3gWFI"
                elif ovs_version == "13":
                    return "1E7-pf6vfrPrIXrGQu2ihGERYkT8vimi2gaRL6q4VAlM"
            elif rhel == "8":
                if ovs_version == "11":
                    return "1kVH-oNQIoJRR_VKFaEdxTDqkJOfUoraTdpWfQqBvNZk"
                elif ovs_version == "12":
                    return "1HW06DhbzTg9Kg36LZeDaRnTex8VQ3M3AAqCR3B7ok0U"
                elif ovs_version == "13":
                    return "1SwDhkvTyizWBxLqHUEbMTHD7zFpak-Qd7FsA1dFFtpQ"
        elif self.nic == "i40e":
            if rhel == "7":
                if ovs_version == "11":
                    return ""
                elif ovs_version == "12":
                    return ""
                elif ovs_version == "13":
                    return ""
            elif rhel == "8":
                if ovs_version == "11":
                    return ""
                elif ovs_version == "12":
                    return ""
                elif ovs_version == "13":
                    return ""
        elif self.nic == "ixgbe":
            if rhel == "7":
                if ovs_version == "11":
                    return ""
                elif ovs_version == "12":
                    return ""
                elif ovs_version == "13":
                    return ""
            elif rhel == "8":
                if ovs_version == "11":
                    return ""
                elif ovs_version == "12":
                    return ""
                elif ovs_version == "13":
                    return ""
        elif self.nic == "qede":
            if rhel == "7":
                if ovs_version == "11":
                    return ""
                elif ovs_version == "12":
                    return ""
                elif ovs_version == "13":
                    return ""
            elif rhel == "8":
                if ovs_version == "11":
                    return ""
                elif ovs_version == "12":
                    return ""
                elif ovs_version == "13":
                    return ""
        elif self.nic == "bnxt_en":
            if rhel == "7":
                if ovs_version == "11":
                    return ""
                elif ovs_version == "12":
                    return ""
                elif ovs_version == "13":
                    return ""
            elif rhel == "8":
                if ovs_version == "11":
                    return ""
                elif ovs_version == "12":
                    return ""
                elif ovs_version == "13":
                    return ""
        else:
            return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gating test results to Google sheets')
    parser.add_argument('--sheet', nargs=1, type=str, help='Test Result Sheet', required=True)
    #parser.add_argument('--nic', nargs=1, type=str, help='NIC', required=True)

    args = parser.parse_args()
    gating_report_sheet = GatingReport(args)
