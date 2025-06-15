import requests
import tweepy
from io import BytesIO

# Function to post an image to Twitter using Tweepy
def post_image_to_twitter(image_url, access_token, access_token_secret, consumer_key, consumer_secret):
    """
    Post an image to Twitter.

    :param image_url: URL of the image to be posted
    :param access_token: Twitter Access Token
    :param access_token_secret: Twitter Access Token Secret
    :param consumer_key: Twitter Consumer Key
    :param consumer_secret: Twitter Consumer Secret
    :return: Response of the post request
    """
    try:
        # Authenticate with Twitter using Tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # Download the image from the image URL
        img_data = requests.get(image_url).content
        with open("temp_image.jpg", 'wb') as f:
            f.write(img_data)

        # Post image to Twitter
        status = "Check out this AI-generated image!"  # Customize your tweet caption
        api.update_with_media("temp_image.jpg", status=status)

        return {'status': 'success', 'message': 'Image posted to Twitter'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

