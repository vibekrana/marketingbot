import requests
import jwt  # PyJWT library to decode the ID token

# Define your variables
authorization_code = "AQR_vtyO0eeBT2pPMQR2SPa5dIn4eRNBOa_MPkL7781Zzyfy-r0xkvtacnkbHjX3ZhcH4m-WXU_6aRc9VU0PABxurgqcO60pyMCdGxpavqJa5VCa6yoYk6BRIVM8e9Ng4oXT-Qejz0RApMYw7AMyEDocfh4tbs_dygwejFPfto_0ptD2HopVO5T97TQqxEMaieBEB0ZUfoV-z78SmBU"  # Replace with the code you received
redirect_uri = "http://marketing-bot-frontend.s3-website.ap-south-1.amazonaws.com/login"
client_id = "77h0r5b7lbjfra"  # Your LinkedIn Client ID
client_secret = "WPL_AP1.01WxyfU02MztUpCt.Tul42Q=="  # Your LinkedIn Client Secret

# Token request URL
token_url = "https://www.linkedin.com/oauth/v2/accessToken"

# Prepare the data for the request
data = {
    'grant_type': 'authorization_code',  # Required for authorization code flow
    'code': authorization_code,  # The authorization code you received
    'redirect_uri': redirect_uri,  # Same redirect URI used in the authorization URL
    'client_id': client_id,        # Your LinkedIn Client ID
    'client_secret': client_secret # Your LinkedIn Client Secret
}

# Send the POST request to get the access token and ID token
response = requests.post(token_url, data=data)

if response.status_code == 200:
    # Parse the response to get the access token and ID token
    token_data = response.json()
    access_token = token_data['access_token']
    id_token = token_data.get('id_token')  # ID token (if available)
    print("Access Token:", access_token)
    print("ID Token:", id_token)

    # Decode the ID token to extract user profile information
    decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})  # Decode without verification for now
    print("Decoded ID Token:", decoded_id_token)
    
    # Extract the LinkedIn user ID (which can be used as the Person URN)
    person_id = decoded_id_token.get('sub')  # The 'sub' claim contains the LinkedIn user ID
    if person_id:
        person_urn = f"urn:li:person:{person_id}"
        print(f"Your LinkedIn Person URN: {person_urn}")
    else:
        print("Person URN not found in the ID token.")
else:
    print("Failed to get access token:", response.status_code, response.text)
