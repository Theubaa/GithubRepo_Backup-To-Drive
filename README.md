# 🗂️ GitHub to Google Drive Backup

This Python script automates the process of backing up GitHub repositories by downloading them as `.zip` files and uploading them to a specified folder on Google Drive.

## 📌 Features

- Authenticates with GitHub using a personal access token
- Supports both user and organization repositories
- Downloads repositories as `.zip` files
- Uploads them to a Google Drive folder
- Skips already uploaded repositories to avoid duplication
- Uses Google OAuth2 for secure Drive access

---

## 🚀 Requirements

- Python 3.7 or higher
- GitHub personal access token
- Google Drive API credentials (`credentials.json`)
- `.env` file with config variables

---

## 🧪 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/github-to-drive-backup.git
cd github-to-drive-backup
2. Install dependencies
bash

pip install -r requirements.txt
Create a requirements.txt file with the following content:

txt

requests
tqdm
python-dotenv
google-auth
google-auth-oauthlib
google-api-python-client
⚙️ Configuration
3. Create a .env file in the project root:
env

GITHUB_USERNAME=your-github-username
GITHUB_TOKEN=your-github-token
ORG_NAMES=org1,org2            # Optional, comma-separated
SCOPES=https://www.googleapis.com/auth/drive.file
GDRIVE_FOLDER_NAME=GitHub Backups
🔐 Google Drive API Setup
Go to Google Cloud Console

Create a project (if you don’t have one)

Enable the Google Drive API

Create OAuth 2.0 Client ID credentials

Download the credentials.json file

Place it in the root directory of the project

The script will guide you through browser-based authentication on first run and save token.json for future use.

▶️ How to Run
bash

python backup.py
The script will:

Fetch your user and organization repositories

Download them as .zip files

Upload them to your Google Drive folder

Remove local .zip files after upload

📁 Output Example
Your Google Drive folder structure:

python

GitHub Backups/
├── repo-one.zip
├── repo-two.zip
├── org-repo-one.zip
└── ...
♻️ Notes
Repositories already uploaded to Drive are skipped automatically.

token.json stores your Drive credentials after the first login.

All temporary .zip files are deleted after upload.

🧹 Cleanup
Temporary files are auto-deleted, but you can manually delete:

token.json (if you want to re-authenticate)

.env (to remove sensitive tokens)

📄 License
MIT License

🙏 Acknowledgments
Thanks to Python, GitHub API, and Google Drive API for making this automation possible.

yaml

---

Let me know if you'd like:
- Badges (e.g. Python version, license)
- A logo/banner
- A GitHub Actions workflow to run this on a schedule
