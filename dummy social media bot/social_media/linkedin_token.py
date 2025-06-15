import requests

# Define your variables
authorization_code = "AQSCFCJDfxS_lmIvYX3R1bNSn7mgVleYXvowjl8frZRER-K8q6VjRnpIXEo2qTv8iXRZOB2_HhOpog-QshufLbcOBH4072KTYWvLD22YhWAyHH8Rgw-GMhHiQdRI_oVGBQjQJDFVbHVuLvJ06K9hSBiITM7f3xlw2aSaVwhlZO-s__jyYykbV_8LFaOYjwNQf6E9OpaUKlpFUz3-2qo"  # Replace with the code from the URL
redirect_uri = "http://marketing-bot-frontend.s3-website.ap-south-1.amazonaws.com/login"
client_id = "786b6xeqo1bp5e"  # Your LinkedIn Client ID
client_secret = "WPL_AP1.TupcHy7ZhYwsAloM.Qx4Y0A=="  # Your LinkedIn Client Secret

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

# Check if the request was successful
if response.status_code == 200:
    # Parse the response to get the access token and ID token
    token_data = response.json()
    access_token = token_data['access_token']
    id_token = token_data.get('id_token')  # ID token (if available)
    print("Access Token:", access_token)
    print("ID Token:", id_token)
else:
    print("Failed to get access token:", response.status_code, response.text)
