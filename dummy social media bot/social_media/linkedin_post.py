import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the LinkedIn access token and Person URN from environment variables
access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')  # Get the access token from the .env file
person_urn = os.getenv('LINKEDIN_PERSON_URN')  # Get the Person URN from the .env file

def post_images_to_linkedin(image_urls, caption):
    """Post selected number of images (1, 2, or 3) to LinkedIn."""
    print('Starting LinkedIn posting...')

    try:
        # ✅ 1️⃣ Register upload for each image and create asset URNs
        media_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }

        asset_urns = []  # List to store asset URNs for each image

        # Register each image for upload
        for image_url in image_urls:
            # Register the image upload with LinkedIn
            register_body = {
                "registerUploadRequest": {
                    "owner": person_urn,
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }

            reg_response = requests.post(media_url, json=register_body, headers=headers)
            reg_response.raise_for_status()

            reg_data = reg_response.json()
            upload_url = reg_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = reg_data['value']['asset']

            print(f"Registered asset: {asset_urn}")

            # ✅ 2️⃣ Upload the binary image to uploadUrl for each image
            img_data = requests.get(image_url).content

            upload_headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }
            upload_response = requests.put(upload_url, data=img_data, headers=upload_headers)

            if upload_response.status_code not in [200, 201]:
                raise Exception(f"Failed to upload image: {upload_response.text}")

            print(f"Uploaded image to LinkedIn. Asset: {asset_urn}")

            # Add asset URN to the list for use in the post
            asset_urns.append(asset_urn)

        # ✅ 3️⃣ Create the post using the asset URNs (multiple images)
        post_url = 'https://api.linkedin.com/v2/ugcPosts'
        post_body = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": caption  # Use the caption generated from ContentGenerator
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {"status": "READY", "media": asset_urn} for asset_urn in asset_urns  # Add each asset URN
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # Send the request to create the post
        post_response = requests.post(post_url, json=post_body, headers=headers)
        post_response.raise_for_status()

        return {'status': 'success', 'message': 'All images posted to LinkedIn'}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# Example usage:
def handle_user_post_choice(num_images, prompt):
    """Handle image generation and posting based on user input."""
    # Assuming the image URLs are already retrieved from S3 after the images are generated
    # Example list of S3 image URLs (you already have these URLs after image generation)
    image_urls = [
        "https://your-bucket-name.s3.amazonaws.com/generated_image_1.png",
        "https://your-bucket-name.s3.amazonaws.com/generated_image_2.png",
        "https://your-bucket-name.s3.amazonaws.com/generated_image_3.png",
        # Add more image URLs as needed
    ]
    
    # Generate caption (ContentGenerator logic already handled)
    caption = f"Here are the generated images for the prompt: {prompt}"

    # Call the LinkedIn posting function
    response = post_images_to_linkedin(image_urls, caption)
    return response

# Example: User selects 3 images
response = handle_user_post_choice(3, "Sample prompt text here")
print(response)
