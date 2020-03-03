import argparse
from GoogleSheet import GoogleSheet
from GoogleDrive import GoogleDrive

def read_resultsheet(resultsheetId):
    res = {}
    GSheet = GoogleSheet()
    all_sheet_titles = GSheet.get_sheet_titles(resultsheetId)
    
    for title in all_sheet_titles:
        sheet_data = GSheet.get_batch_data(resultsheetId, title + "!A1:J32")
        res[title] = sheet_data['valueRanges'][0]['values']
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OVS Results- Google sheets')
    parser.add_argument('--sheet', nargs=1, type=str, help='Test Result Sheet', required=True)

    args = parser.parse_args()

    resultsheet = str(args.sheet[0])
    mydata = read_resultsheet(resultsheet)
    #print(mydata)
    for title in mydata:
        print("\n", title, ":")
        print(mydata[title])

