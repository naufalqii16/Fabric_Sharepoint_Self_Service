# services/sharepoint_service.py
import requests
from io import BytesIO
from typing import Dict, List, Optional
from services.auth import auth
from services.preprocessing import list_all_files
import re

class SharePointService:
    def __init__(self, site_id: str, drive_id: str):
        self.site_id = site_id
        self.drive_id = drive_id
        self.token = auth.get_graph_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def get_file_metadata(self, FolderPath: str, FilePattern: str) -> Dict:
        """
        Get file metadata without downloading
        Returns: {
            'file_id': str,
            'file_name': str,
            'file_size': int,
            'download_url': str,
            'parent_folder_id': str
        }
        """

        folder_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/root:/{FolderPath}:/children"
        
        all_files = list_all_files(folder_url, FolderPath, self.headers, 
                                    self.site_id, self.drive_id)
        
        matched = [f for f in all_files if re.fullmatch(FilePattern, f["name"])]
        
        if not matched:
            raise ValueError(f"No files matched pattern: {FilePattern}")
        
        # Handle multiple matches
        if len(matched) > 1:
            root_only = all(f.get("folder_name") is None for f in matched)
            if root_only:
                matched = [matched[0]]  # Take first root file
        
        return matched[0]
    
    def download_file(self, download_url: str) -> BytesIO:
        """Download file content as BytesIO"""
        response = requests.get(download_url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Download failed: HTTP {response.status_code}")
        
        return BytesIO(response.content)
    
    def create_backup(self, file_id: str, file_name: str, 
                     parent_folder_id: str, backup_FolderPath: str):
        """Create backup copy of file"""
        from services.preprocessing import backup_file_in_sharepoint
        
        return backup_file_in_sharepoint(
            file_id=file_id,
            file_name=file_name,
            parent_folder_id=parent_folder_id,
            headers=self.headers,
            SITE_ID=self.site_id,
            DRIVE_ID=self.drive_id,
            backup_FolderPath=backup_FolderPath
        )