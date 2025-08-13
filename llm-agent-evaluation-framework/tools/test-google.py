import argparse
import json
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from langchain_core.tools import tool
import streamlit as st
import os
import io

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

@st.cache_resource
def get_google_drive_service():
    """
    Gets the Google Drive credentials with the scope of full access to Drive files
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

service = get_google_drive_service()

@tool
def search_file(query: str) -> list:
    try:
        results = service.files().list(q=f"mimeType!='application/vnd.google-apps.folder' and {query}", spaces='drive', fields="files(id, name)").execute()
        return results.get('files', [])
    except Exception as e:
        return f"Failed to search Google Drive: {e}"

@tool
def download_file(file_id: str, file_name: str, mime_type: str = 'text/plain') -> str:
    try:
        directory = "data"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        request = service.files().export_media(fileId=file_id, mimeType=mime_type)
        file_path = f"{directory}/{file_name}"
        with io.FileIO(file_path, 'wb') as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        
        return f"File downloaded to {file_path}"
    except Exception as e:
        return f"Error downloading the file: {e}"

@tool
def upload_file(file_path: str, folder_id: str = None) -> str:
    try:
        file_metadata = {'name': file_path.split("/")[-1]}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return f"File uploaded with ID: {file.get('id')}"
    except Exception as e:
        return f"Error uploading the file: {e}"

@tool
def delete_file(file_id: str) -> str:
    try:
        service.files().delete(fileId=file_id).execute()
        return f"File with ID {file_id} has been deleted."
    except Exception as e:
        return f"Error deleting the file: {e}"

@tool
def update_file(file_id: str, new_file_path: str) -> str:
    try:
        media = MediaFileUpload(new_file_path, resumable=True)
        updated_file = service.files().update(fileId=file_id, media_body=media).execute()
        return f"File with ID {file_id} has been updated."
    except Exception as e:
        return f"Error updating the file: {e}"

@tool
def search_folder(query: str) -> list:
    try:
        results = service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name contains '{query}'",
                                    spaces='drive', fields="files(id, name)").execute()
        return results.get('files', [])
    except Exception as e:
        return f"Error searching folders: {e}"

@tool
def create_folder(folder_name: str, parent_folder_id: str = None) -> str:
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return f"Folder created with ID: {folder.get('id')}"
    except Exception as e:
        return f"Error creating the folder: {e}"

@tool
def delete_folder(folder_id: str) -> str:
    try:
        service.files().delete(fileId=folder_id).execute()
        return f"Folder with ID {folder_id} has been deleted."
    except Exception as e:
        return f"Error deleting the folder: {e}"

@tool
def create_text_file(content: str, file_name: str) -> str:
    try:
        directory = "data"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = f"{directory}/{file_name}"
        with open(file_path, "w") as file:
            file.write(content)
        return file_path
    except Exception as e:
        return f"Error creating the text file: {e}"

# 函数映射
available_drive_functions = {
    "search_file": search_file,
    "download_file": download_file,
    "upload_file": upload_file,
    "delete_file": delete_file,
    "update_file": update_file,
    "search_folder": search_folder,
    "create_folder": create_folder,
    "delete_folder": delete_folder,
    "create_text_file": create_text_file
}
