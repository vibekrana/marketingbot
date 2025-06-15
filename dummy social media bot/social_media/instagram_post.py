import requests

# Function to post an image to Instagram using Instagram Graph API
def post_image_to_instagram(image_url, access_token, user_id):
    """
    Post an image to Instagram.

    :param image_url: URL of the image to be posted
    :param access_token: Instagram Graph API access token
    :param user_id: Instagram Business User ID
    :return: Response of the post request
    """
    try:
        # Step 1: Upload the image to Instagram Media
        media_url = f'https://graph.facebook.com/v13.0/{user_id}/media'
        media_data = {
            'image_url': image_url,
            'access_token': access_token,
        }
        media_response = requests.post(media_url, data=media_data)
        media_id = media_response.json().get('id')

        # Step 2: Publish the image to Instagram
        if media_id:
            publish_url = f'https://graph.facebook.com/v13.0/{user_id}/media_publish'
            publish_data = {
                'creation_id': media_id,
                'access_token': access_token,
            }
            publish_response = requests.post(publish_url, data=publish_data)

            if publish_response.status_code == 200:
                return {'status': 'success', 'message': 'Image posted to Instagram'}
            else:
                return {'status': 'error', 'message': 'Failed to publish image'}
        else:
            return {'status': 'error', 'message': 'Failed to upload media'}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}
