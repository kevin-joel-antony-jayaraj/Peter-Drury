import json
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
KEYS_FILE = BASE_DIR / "keys.env"
load_dotenv(KEYS_FILE)


from apiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "token.json"
SPACE_NAME = os.getenv("GOOGLE_CHAT_SPACE_NAME", "")


SCOPES = [
    "https://www.googleapis.com/auth/chat.messages.create",
    "https://www.googleapis.com/auth/chat.spaces.create",
]


def normalize_space_name(space_name: str) -> str:
    if not space_name:
        raise ValueError("GOOGLE_CHAT_SPACE_NAME is not set")

    cleaned = space_name.strip().split("?", 1)[0]
    if cleaned.startswith("spaces/"):
        return cleaned
    return f"spaces/{cleaned}"


def get_user_credentials():
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_FILE.write_text(json.dumps({
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
                "expiry": creds.expiry.isoformat() if creds.expiry else None,
            }), encoding="utf-8")
            return creds

    if not CLIENT_SECRET_FILE.exists():
        raise FileNotFoundError(
            "client_secret.json not found. Create an OAuth Desktop client in Google Cloud Console."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_chat_service():
    creds = get_user_credentials()
    return build("chat", "v1", credentials=creds)


def send_message(text: str, parent: str | None = None):
    chat = get_chat_service()
    parent_name = normalize_space_name(parent or SPACE_NAME)
    return chat.spaces().messages().create(
        parent=parent_name,
        body={"text": text},
    ).execute()