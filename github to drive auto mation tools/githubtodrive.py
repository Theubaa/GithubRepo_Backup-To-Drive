import os
import requests
import shutil
from tqdm import tqdm
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === Load .env ===
load_dotenv()

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAMES = os.getenv("ORG_NAMES", "").split(",")
SCOPES = [os.getenv("SCOPES")]
GDRIVE_FOLDER_NAME = os.getenv("GDRIVE_FOLDER_NAME", "GitHub Backups")

# === Google Drive Auth ===
def authenticate_gdrive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

# === Create folder in Drive ===
def create_drive_folder(service, name):
    results = service.files().list(q=f"name='{name}' and mimeType='application/vnd.google-apps.folder'",
                                   spaces='drive').execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

# === Check if file already exists in Drive folder ===
def file_exists_in_drive(service, folder_id, filename):
    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive').execute()
    return len(results.get('files', [])) > 0

# === Upload file ===
def upload_to_drive(service, file_path, folder_id):
    file_name = os.path.basename(file_path)
    if file_exists_in_drive(service, folder_id, file_name):
        print(f"🔁 Skipped (already uploaded): {file_name}")
        return
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/zip', resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ Uploaded: {file_name}")

# === Fetch GitHub repos ===
def fetch_repos(user_or_org, is_org=False):
    url = f"https://api.github.com/{'orgs' if is_org else 'users'}/{user_or_org}/repos"
    repos = []
    page = 1
    while True:
        resp = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"}, params={'page': page, 'per_page': 100})
        if resp.status_code != 200:
            print(f"❌ Failed to fetch repos for {user_or_org} (Status {resp.status_code})")
            break
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

# === Main Logic ===
def main():
    print("🚀 Starting GitHub to Google Drive backup...")
    service = authenticate_gdrive()
    folder_id = create_drive_folder(service, GDRIVE_FOLDER_NAME)

    all_repos = fetch_repos(GITHUB_USERNAME)
    for org in ORG_NAMES:
        if org.strip():
            all_repos += fetch_repos(org.strip(), is_org=True)

    os.makedirs("temp_repos", exist_ok=True)

    for repo in tqdm(all_repos, desc="Processing Repos"):
        zip_url = repo["html_url"] + "/archive/refs/heads/" + repo["default_branch"] + ".zip"
        repo_name = repo["name"]
        zip_path = os.path.join("temp_repos", f"{repo_name}.zip")

        try:
            with requests.get(zip_url, stream=True) as r:
                if r.status_code != 200:
                    print(f"⚠️ Skipped {repo_name} (no zip available)")
                    continue
                with open(zip_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
        except Exception as e:
            print(f"❌ Error downloading {repo_name}: {e}")
            continue

        upload_to_drive(service, zip_path, folder_id)
        os.remove(zip_path)

    shutil.rmtree("temp_repos")
    print("🎉 Backup completed.")

if __name__ == "__main__":
    main()
