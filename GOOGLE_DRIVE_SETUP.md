# 🔐 Google Drive API Setup Guide

This guide helps you set up Google Drive API integration for permanent data persistence in your cloud-deployed Billing & Estimate Manager.

## 🎯 Overview

The Google Drive integration provides:
- **Permanent data storage** across sessions
- **Automatic database sync** to/from Google Drive
- **Full SQLite functionality** with cloud backup
- **Same features as local app** but cloud-persistent

## 🚀 Quick Setup (2 Options)

### Option 1: Service Account (Recommended for Production)

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project ID

#### Step 2: Enable Google Drive API
1. In the Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click "Enable"

#### Step 3: Create Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter name: `billing-estimate-manager`
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

#### Step 4: Generate Service Account Key
1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Download the JSON file

#### Step 5: Configure Streamlit Secrets
1. In your Streamlit Cloud app settings, go to "Secrets"
2. Add the following configuration:

```toml
[google_drive]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
client_email = "billing-estimate-manager@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/billing-estimate-manager%40your-project-id.iam.gserviceaccount.com"
```

**Important**: Replace all placeholder values with actual values from your downloaded JSON file.

### Option 2: OAuth 2.0 (For Personal Use)

#### Step 1: Create OAuth 2.0 Credentials
1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Select "Web application"
4. Add your Streamlit app URL to "Authorized redirect URIs":
   - For Streamlit Cloud: `https://your-app-name.streamlit.app`
   - For local testing: `http://localhost:8501`

#### Step 2: Configure OAuth Secrets
```toml
[google_oauth]
client_id = "your-oauth-client-id.apps.googleusercontent.com"
client_secret = "your-oauth-client-secret"
redirect_uri = "https://your-app-name.streamlit.app"
```

## 🚀 Deployment Instructions

### Deploy Persistent Version

1. **Deploy to Streamlit Cloud**:
   - Repository: `your-username/billing-estimate-tool-v2`
   - Branch: `main`
   - **Main file**: `app_persistent.py` ⚠️ **Use persistent version!**

2. **Add Secrets Configuration**:
   - Go to app settings in Streamlit Cloud
   - Add your Google Drive credentials in "Secrets" section

3. **Test Connection**:
   - App will show authentication status in sidebar
   - Use "Sync From Drive" to download existing data
   - Use "Sync To Drive" to upload data

## 🔄 How It Works

### Data Flow
```
Local SQLite ↔ Google Drive ↔ Cloud App
```

1. **First Launch**: Downloads existing database from Google Drive
2. **Normal Usage**: Works with local SQLite (fast performance)
3. **Auto-Sync**: Automatically uploads changes to Google Drive
4. **Manual Sync**: User can trigger sync at any time

### File Structure in Google Drive
```
Google Drive/
└── Billing_Estimate_Manager/
    ├── billing_database.db        # Main database
    ├── billing_backup_20241201.json  # JSON backups
    └── billing_backup_20241202.json
```

## ⚙️ Configuration Options

### Auto-Sync Settings
- **Auto-sync enabled**: Changes automatically uploaded to Google Drive
- **Manual sync**: User controls when to sync data
- **Sync indicators**: Shows sync status in sidebar

### Database Features
- **Full SQLite**: All original database features
- **Relationships**: Foreign keys and constraints preserved
- **Performance**: Local operations remain fast
- **Backup**: Automatic JSON backups to Google Drive

## 🔧 Troubleshooting

### Common Issues

#### "Google Drive Not Connected"
- **Solution**: Check that secrets are properly configured
- **Check**: Verify JSON formatting in secrets
- **Test**: Service account email has correct permissions

#### "Authentication Failed"
- **Solution**: Regenerate credentials in Google Cloud Console
- **Check**: OAuth redirect URIs match your app URL
- **Verify**: Google Drive API is enabled

#### "Sync Failed"
- **Solution**: Check Google Drive storage quota
- **Verify**: Service account has Drive access
- **Check**: Network connectivity

### Debug Steps
1. Check sidebar for authentication status
2. Verify Google Cloud Console settings
3. Test with OAuth first (simpler setup)
4. Check Streamlit Cloud logs for errors

## 🆚 Version Comparison

| Feature | Session (`app_cloud.py`) | Persistent (`app_persistent.py`) |
|---------|-------------------------|----------------------------------|
| **Data Storage** | Session State | Google Drive + SQLite |
| **Persistence** | Session Only | Permanent |
| **Performance** | Fast | Fast (local SQLite) |
| **Setup** | No setup required | Google API setup required |
| **Sync** | Manual export/import | Automatic sync |
| **Database** | In-memory | Full SQLite |
| **Offline** | No | Yes (with local cache) |

## 📝 Best Practices

### Security
- **Never commit credentials** to git repository
- **Use service accounts** for production deployments
- **Rotate keys regularly** (every 90 days)
- **Monitor API usage** in Google Cloud Console

### Performance
- **Enable auto-sync** for real-time backup
- **Manual sync** for better performance during heavy usage
- **Local operations** remain fast (SQLite)

### Backup Strategy
- **Automatic JSON backups** created on major changes
- **Database snapshots** stored in Google Drive
- **Version history** maintained automatically

## 🎉 Ready to Deploy!

Once configured, your app will have:
- ✅ **Permanent data persistence**
- ✅ **Automatic cloud backup**
- ✅ **Full database functionality**
- ✅ **Same performance as local app**
- ✅ **Cross-device data access**

Your persistent Billing & Estimate Manager is ready for production use! 🚀