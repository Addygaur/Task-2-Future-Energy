from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import io
import re

# Set up credentials
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = None
if os.path.exists('credentials.json'):
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
else:
    print("Credentials file 'credentials.json' not found.")

# Build the Drive API service
service = build('drive', 'v3', credentials=creds)

# Function to download file
def download_file(file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, mode='wb')
    downloader = io.BytesIO(request.execute())
    downloader.seek(0)
    fh.write(downloader.read())

# Function to download folder recursively
def download_folder(folder_id, folder_name):
    os.makedirs(folder_name, exist_ok=True)
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])
    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            sub_folder_name = os.path.join(folder_name, item['name'])
            download_folder(item['id'], sub_folder_name)
        else:
            download_file(item['id'], os.path.join(folder_name, item['name']))

# Main function
def main():
    folder_name = input("Enter the name for your folder:  ").strip()
    if folder_name:
        folder_link = input("Enter the public link to the Google Drive folder: ")
        folder_id_match = re.search(r'[-\w]{25,}', folder_link)
        if folder_id_match:
            folder_id = folder_id_match.group(0)
            download_folder(folder_id, folder_name)
            print(f"Folder '{folder_name}' downloaded successfully.")
        else:
            print("Invalid folder link format.")
    else:
        print("Folder name cannot be empty.")

if __name__ == '__main__':
    main()
