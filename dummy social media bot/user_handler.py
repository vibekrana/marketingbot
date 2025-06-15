import json
import jwt
import time
import os
import requests
from dotenv import load_dotenv

# ✅ Load .env file for your LinkedIn keys
load_dotenv()

SECRET_KEY = "my-secure-secret-key-12345"

# ✅ Read LinkedIn OAuth config
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")

class UserHandler:
    def login(self, context):
        request = context["request"]
        body = request.get("body")

        if not body:
            raise Exception("Request body is empty")

        data = json.loads(body) if isinstance(body, str) else body
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise Exception("Username and password are required")

        if username == "craftingbrain" and password == "rohith":
            token_payload = {
                "username": username,
                "exp": int(time.time()) + 3600
            }
            token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

            return {
                "token": token,
                "user": {"username": username}
            }
        else:
            raise Exception("Invalid username or password")

    def linkedin_callback(self, context):
        """
        ✅ NEW: Handles LinkedIn OAuth callback.
        Exchanges 'code' for 'access_token'
        """
        request = context["request"]
        body = request.get("body")

        if not body:
            raise Exception("Request body is empty")

        data = json.loads(body) if isinstance(body, str) else body
        code = data.get("code")

        if not code:
            raise Exception("Authorization code is missing")

        # ✅ Make request to LinkedIn to exchange code
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": LINKEDIN_REDIRECT_URI,
            "client_id": LINKEDIN_CLIENT_ID,
            "client_secret": LINKEDIN_CLIENT_SECRET
        }

        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        token_data = response.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise Exception(f"Failed to get access token: {token_data}")

        return {"access_token": access_token}
