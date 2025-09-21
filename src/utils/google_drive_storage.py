"""
Google Drive Storage Manager for Permanent Persistence

This module provides permanent data persistence using Google Drive API,
allowing data to persist across sessions in cloud deployments.
"""

import streamlit as st
import json
import io
import sqlite3
import tempfile
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import base64

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
    from googleapiclient.errors import HttpError
except ImportError:
    st.error("Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GoogleDriveManager:
    """Manages data persistence using Google Drive as cloud storage"""

    # These scopes allow read/write access to Google Drive
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self):
        self.service = None
        self.database_file_id = None
        self.app_folder_id = None

    def setup_credentials_from_secrets(self) -> bool:
        """Setup credentials from Streamlit secrets"""
        try:
            # Check if secrets are configured
            if "google_drive" not in st.secrets:
                return False

            secrets = st.secrets["google_drive"]

            # Create credentials from secrets
            creds_info = {
                "type": secrets["type"],
                "project_id": secrets["project_id"],
                "private_key_id": secrets["private_key_id"],
                "private_key": secrets["private_key"],
                "client_email": secrets["client_email"],
                "client_id": secrets["client_id"],
                "auth_uri": secrets["auth_uri"],
                "token_uri": secrets["token_uri"],
                "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
                "client_x509_cert_url": secrets["client_x509_cert_url"]
            }

            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_info(
                creds_info, scopes=self.SCOPES
            )

            self.service = build('drive', 'v3', credentials=creds)
            return True

        except Exception as e:
            st.error(f"Error setting up Google Drive credentials: {str(e)}")
            return False

    def setup_oauth_flow(self) -> Optional[str]:
        """Setup OAuth flow for user authentication"""
        try:
            if "google_oauth" not in st.secrets:
                st.error("Google OAuth credentials not found in secrets")
                return None

            client_config = {
                "web": {
                    "client_id": st.secrets["google_oauth"]["client_id"],
                    "client_secret": st.secrets["google_oauth"]["client_secret"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]]
                }
            }

            flow = Flow.from_client_config(
                client_config,
                scopes=self.SCOPES,
                redirect_uri=st.secrets["google_oauth"]["redirect_uri"]
            )

            auth_url, _ = flow.authorization_url(prompt='consent')
            return auth_url

        except Exception as e:
            st.error(f"Error setting up OAuth flow: {str(e)}")
            return None

    def handle_oauth_callback(self, auth_code: str) -> bool:
        """Handle OAuth callback and store credentials"""
        try:
            if "google_oauth" not in st.secrets:
                return False

            client_config = {
                "web": {
                    "client_id": st.secrets["google_oauth"]["client_id"],
                    "client_secret": st.secrets["google_oauth"]["client_secret"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]]
                }
            }

            flow = Flow.from_client_config(
                client_config,
                scopes=self.SCOPES,
                redirect_uri=st.secrets["google_oauth"]["redirect_uri"]
            )

            flow.fetch_token(code=auth_code)

            # Store credentials in session state
            st.session_state.google_drive_creds = {
                'token': flow.credentials.token,
                'refresh_token': flow.credentials.refresh_token,
                'token_uri': flow.credentials.token_uri,
                'client_id': flow.credentials.client_id,
                'client_secret': flow.credentials.client_secret,
                'scopes': flow.credentials.scopes
            }

            self.service = build('drive', 'v3', credentials=flow.credentials)
            return True

        except Exception as e:
            st.error(f"Error handling OAuth callback: {str(e)}")
            return False

    def load_credentials_from_session(self) -> bool:
        """Load credentials from session state"""
        try:
            if 'google_drive_creds' not in st.session_state:
                return False

            creds_dict = st.session_state.google_drive_creds
            creds = Credentials(
                token=creds_dict['token'],
                refresh_token=creds_dict['refresh_token'],
                token_uri=creds_dict['token_uri'],
                client_id=creds_dict['client_id'],
                client_secret=creds_dict['client_secret'],
                scopes=creds_dict['scopes']
            )

            # Refresh token if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update session state with new token
                st.session_state.google_drive_creds['token'] = creds.token

            self.service = build('drive', 'v3', credentials=creds)
            return True

        except Exception as e:
            st.error(f"Error loading credentials: {str(e)}")
            return False

    def is_authenticated(self) -> bool:
        """Check if Google Drive is authenticated"""
        return self.service is not None

    def create_app_folder(self) -> bool:
        """Create application folder in Google Drive"""
        try:
            # Search for existing folder
            results = self.service.files().list(
                q="name='Billing_Estimate_Manager' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()

            if results['files']:
                self.app_folder_id = results['files'][0]['id']
                return True

            # Create new folder
            folder_metadata = {
                'name': 'Billing_Estimate_Manager',
                'mimeType': 'application/vnd.google-apps.folder'
            }

            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            self.app_folder_id = folder.get('id')
            return True

        except Exception as e:
            st.error(f"Error creating app folder: {str(e)}")
            return False

    def upload_database(self, db_path: str) -> bool:
        """Upload SQLite database to Google Drive"""
        try:
            if not self.app_folder_id:
                if not self.create_app_folder():
                    return False

            # Check if database file already exists
            results = self.service.files().list(
                q=f"name='billing_database.db' and parents in '{self.app_folder_id}'",
                fields="files(id, name)"
            ).execute()

            # Read database file
            with open(db_path, 'rb') as db_file:
                media = MediaIoBaseUpload(io.BytesIO(db_file.read()), mimetype='application/octet-stream')

            if results['files']:
                # Update existing file
                self.database_file_id = results['files'][0]['id']
                updated_file = self.service.files().update(
                    fileId=self.database_file_id,
                    media_body=media
                ).execute()
            else:
                # Create new file
                file_metadata = {
                    'name': 'billing_database.db',
                    'parents': [self.app_folder_id]
                }

                uploaded_file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                self.database_file_id = uploaded_file.get('id')

            return True

        except Exception as e:
            st.error(f"Error uploading database: {str(e)}")
            return False

    def download_database(self) -> Optional[str]:
        """Download SQLite database from Google Drive"""
        try:
            if not self.app_folder_id:
                if not self.create_app_folder():
                    return None

            # Find database file
            results = self.service.files().list(
                q=f"name='billing_database.db' and parents in '{self.app_folder_id}'",
                fields="files(id, name)"
            ).execute()

            if not results['files']:
                return None  # No database file found

            self.database_file_id = results['files'][0]['id']

            # Download file
            request = self.service.files().get_media(fileId=self.database_file_id)
            downloaded = io.BytesIO()
            downloader = MediaIoBaseDownload(downloaded, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                temp_file.write(downloaded.getvalue())
                return temp_file.name

        except Exception as e:
            st.error(f"Error downloading database: {str(e)}")
            return None

    def backup_data_as_json(self, data: Dict[str, Any]) -> bool:
        """Backup data as JSON to Google Drive"""
        try:
            if not self.app_folder_id:
                if not self.create_app_folder():
                    return False

            # Add timestamp to data
            data['backup_timestamp'] = datetime.now().isoformat()
            json_data = json.dumps(data, indent=2)

            # Create filename with timestamp
            filename = f"billing_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            media = MediaIoBaseUpload(io.BytesIO(json_data.encode()), mimetype='application/json')

            file_metadata = {
                'name': filename,
                'parents': [self.app_folder_id]
            }

            uploaded_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            return True

        except Exception as e:
            st.error(f"Error backing up data: {str(e)}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all backup files in Google Drive"""
        try:
            if not self.app_folder_id:
                if not self.create_app_folder():
                    return []

            results = self.service.files().list(
                q=f"name contains 'billing_backup_' and parents in '{self.app_folder_id}'",
                fields="files(id, name, createdTime, size)",
                orderBy='createdTime desc'
            ).execute()

            return results.get('files', [])

        except Exception as e:
            st.error(f"Error listing backups: {str(e)}")
            return []

    def download_backup(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Download a specific backup file"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            downloaded = io.BytesIO()
            downloader = MediaIoBaseDownload(downloaded, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()

            json_data = downloaded.getvalue().decode('utf-8')
            return json.loads(json_data)

        except Exception as e:
            st.error(f"Error downloading backup: {str(e)}")
            return None


class GoogleDrivePersistentManager:
    """Main manager combining local SQLite with Google Drive sync"""

    def __init__(self):
        self.drive_manager = GoogleDriveManager()
        self.local_db_path = None
        self.is_synced = False

    def authenticate(self) -> bool:
        """Authenticate with Google Drive"""
        # Try service account first (for deployment)
        if self.drive_manager.setup_credentials_from_secrets():
            return True

        # Try loading from session
        if self.drive_manager.load_credentials_from_session():
            return True

        return False

    def get_oauth_url(self) -> Optional[str]:
        """Get OAuth URL for user authentication"""
        return self.drive_manager.setup_oauth_flow()

    def handle_oauth(self, auth_code: str) -> bool:
        """Handle OAuth authentication"""
        return self.drive_manager.handle_oauth_callback(auth_code)

    def sync_from_drive(self) -> Optional[str]:
        """Download database from Google Drive and set up local copy"""
        if not self.drive_manager.is_authenticated():
            return None

        # Download database from Google Drive
        downloaded_db = self.drive_manager.download_database()

        if downloaded_db:
            self.local_db_path = downloaded_db
            self.is_synced = True
            return downloaded_db
        else:
            # Create new database if none exists
            self.local_db_path = tempfile.NamedTemporaryFile(delete=False, suffix='.db').name
            self._init_database()
            return self.local_db_path

    def sync_to_drive(self) -> bool:
        """Upload current database to Google Drive"""
        if not self.drive_manager.is_authenticated() or not self.local_db_path:
            return False

        return self.drive_manager.upload_database(self.local_db_path)

    def _init_database(self):
        """Initialize empty database with schema"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()

        # Create tables (copy from your existing database schema)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                gstin TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                tax_rate DECIMAL(5,2) DEFAULT 18.0,
                default_discount_rate DECIMAL(5,2) DEFAULT 0.0,
                category TEXT,
                unit TEXT DEFAULT 'piece',
                stock_quantity INTEGER DEFAULT 0,
                low_stock_alert INTEGER DEFAULT 5,
                size_mm_length DECIMAL(8,2),
                size_mm_width DECIMAL(8,2),
                size_mm_height DECIMAL(8,2),
                size_inches_length DECIMAL(8,2),
                size_inches_width DECIMAL(8,2),
                size_inches_height DECIMAL(8,2),
                material TEXT,
                finish TEXT,
                color TEXT,
                weight DECIMAL(8,2),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estimate_id TEXT UNIQUE NOT NULL,
                estimate_number TEXT NOT NULL,
                customer_id INTEGER,
                customer_name TEXT NOT NULL,
                customer_email TEXT,
                customer_address TEXT,
                customer_gstin TEXT,
                date DATE NOT NULL,
                due_date DATE,
                notes TEXT,
                terms TEXT,
                subtotal DECIMAL(10,2) NOT NULL,
                global_discount_rate DECIMAL(5,2) DEFAULT 0.0,
                global_discount_amount DECIMAL(10,2) DEFAULT 0.0,
                total_tax DECIMAL(10,2) NOT NULL,
                grand_total DECIMAL(10,2) NOT NULL,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estimate_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estimate_id TEXT NOT NULL,
                item_id INTEGER,
                sku TEXT,
                name TEXT NOT NULL,
                description TEXT,
                quantity DECIMAL(10,3) NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                discount_rate DECIMAL(5,2) DEFAULT 0.0,
                tax_rate DECIMAL(5,2) DEFAULT 18.0,
                line_total DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (estimate_id) REFERENCES estimates (estimate_id),
                FOREIGN KEY (item_id) REFERENCES inventory_items (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_settings (
                id INTEGER PRIMARY KEY,
                business_name TEXT NOT NULL,
                business_address TEXT,
                business_phone TEXT,
                business_email TEXT,
                business_gstin TEXT,
                business_logo_path TEXT,
                estimate_prefix TEXT DEFAULT 'EST',
                estimate_counter INTEGER DEFAULT 1,
                currency_symbol TEXT DEFAULT '₹',
                default_tax_rate DECIMAL(5,2) DEFAULT 18.0,
                smtp_server TEXT,
                smtp_port INTEGER,
                smtp_username TEXT,
                smtp_password TEXT,
                terms_and_conditions TEXT,
                notes_footer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert default business settings
        cursor.execute('''
            INSERT OR IGNORE INTO business_settings
            (id, business_name, business_address, business_phone, business_email, business_gstin, currency_symbol, terms_and_conditions, notes_footer)
            VALUES (1, 'Your Business Name', '123 Business Street\nYour City, State 12345', '+1-555-123-4567', 'info@yourbusiness.com', 'GSTIN123456789', '₹', 'Payment due within 30 days.', 'Thank you for your business!')
        ''')

        conn.commit()
        conn.close()

    def get_local_db_path(self) -> Optional[str]:
        """Get path to local database"""
        return self.local_db_path

    def cleanup(self):
        """Clean up temporary files"""
        if self.local_db_path and os.path.exists(self.local_db_path):
            try:
                os.unlink(self.local_db_path)
            except:
                pass


# Global instance
drive_persistent_manager = GoogleDrivePersistentManager()