import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, List, Any, Optional

class GSheetManager:
    """Utility class for managing Google Sheets integration"""
    
    def __init__(self, credentials_path: str = 'credentials.json'):
        """Initialize the Google Sheets manager
        
        Args:
            credentials_path: Path to the Google service account credentials file
        """
        self.credentials_path = credentials_path
        self._client = None
        
    def connect(self) -> None:
        """Connect to Google Sheets API using service account credentials"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scopes
            )
            self._client = gspread.authorize(credentials)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Google Sheets: {str(e)}")
    
    @property
    def client(self) -> gspread.Client:
        """Get the gspread client, connecting if not already connected"""
        if self._client is None:
            self.connect()
        return self._client
    
    def get_athlete_data(self, spreadsheet_id: str, worksheet_name: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve athlete data from the specified Google Sheet
        
        Args:
            spreadsheet_id: The ID of the Google Sheet (from the URL)
            worksheet_name: Optional name of the worksheet to use (uses first sheet if None)
            
        Returns:
            Dictionary containing athlete information
        """
        try:
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Get the appropriate worksheet
            if worksheet_name:
                worksheet = spreadsheet.worksheet(worksheet_name)
            else:
                worksheet = spreadsheet.sheet1
            
            # Get all records as dictionaries
            all_records = worksheet.get_all_records()
            
            if not all_records:
                raise ValueError("No athlete data found in the spreadsheet")
                
            # For now, just return the first athlete's data
            # In the future, this could be expanded to handle multiple athletes
            return all_records[0]
            
        except Exception as e:
            raise Exception(f"Error retrieving athlete data: {str(e)}")
    
    @staticmethod
    def get_template_structure() -> List[str]:
        """Get the recommended column structure for the athlete spreadsheet"""
        return [
            "First Name", "Last Name", "Email", "Phone", 
            "Address", "City", "State", "Zip", 
            "High School", "Graduation Year", "GPA", 
            "Position", "Height", "Weight", "Achievements", 
            "Stats", "Video Links", "Additional Notes"
        ]