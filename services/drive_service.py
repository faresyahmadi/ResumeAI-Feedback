from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
import os
import pickle
from config.config import GOOGLE_DRIVE_CREDENTIALS, DRIVE_FOLDER_ID, ALLOWED_FILE_TYPES

class DriveService:
    SCOPES = ['https://www.googleapis.com/auth/drive']
    FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    # MIME type mappings
    MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    def __init__(self):
        self.creds = self._get_credentials()
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def _get_credentials(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def upload_file(self, filepath):
        """Upload a file to Google Drive in the specified folder"""
        try:
            file_metadata = {
                'name': os.path.basename(filepath),
                'parents': ['1W1tT96QyKHOyB4FmEkNi58pquXF5EXTR']  # Upload to specific folder
            }
            
            media = MediaFileUpload(
                filepath,
                mimetype=self._get_mime_type(filepath),
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"File uploaded successfully. File ID: {file.get('id')}")
            return file
            
        except Exception as e:
            print(f"Error uploading file to Google Drive: {str(e)}")
            raise

    def _get_mime_type(self, filepath):
        """Get the MIME type of the file based on extension."""
        ext = os.path.splitext(filepath)[1].lower()
        return self.MIME_TYPES.get(ext, 'application/octet-stream')

    def list_files(self):
        """List all files in the specified folder."""
        try:
            results = self.service.files().list(
                q=f"'{self.FOLDER_ID}' in parents",
                fields="files(id, name, createdTime)",
                orderBy="createdTime desc"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []

    def delete_file(self, file_id):
        """Delete a file from Google Drive."""
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"Successfully deleted file: {file_id}")
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

    def get_new_files(self, last_check_time):
        """Get new files uploaded since last check"""
        query = f"'{DRIVE_FOLDER_ID}' in parents and createdTime > '{last_check_time}'"
        results = self.service.files().list(
            q=query,
            fields="files(id, name, createdTime, mimeType)",
            orderBy="createdTime desc"
        ).execute()
        
        files = results.get('files', [])
        return [f for f in files if any(f['name'].lower().endswith(ext) for ext in ALLOWED_FILE_TYPES)]
    
    def download_file(self, file_id):
        """Download a file from Google Drive"""
        request = self.service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file.seek(0)
        return file 