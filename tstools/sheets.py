# Functions for interacting with Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load sheet
def load_sheet(spreadsheet, worksheet, cred_file):
    scope = ['https://spreadsheets.google.com/feeds' + ' ' +'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open(spreadsheet).get_worksheet(worksheet)
    return sheet
