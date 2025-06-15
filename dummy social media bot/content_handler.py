import json
import subprocess
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
from image_generation.image_generator import ImageGenerator
from social_media.instagram_post import post_image_to_instagram
from social_media.twitter_post import post_image_to_twitter
from social_media.linkedin_post import post_images_to_linkedin

# Load environment variables
load_dotenv()

# Path to content_generator.py
CONTENT_GENERATOR_PATH = "content_generation/content_generator.py"

class ContentGenerator:
    def __init__(self):
        self.image_generator = ImageGenerator()

    def run_content_generator(self, theme, num_subtopics, content_type):
        """Run content_generator.py to generate content_details.json."""
        command = f"python {CONTENT_GENERATOR_PATH} --theme \"{theme}\" --num_subtopics {num_subtopics} --content_type {content_type}"
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Content generation failed: {e}")

    def load_content_details(self):
        """Load content details from content_details.json."""
        try:
            with open("content_details.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception("content_details.json not found. Ensure content_generator.py ran successfully.")
        except json.JSONDecodeError:
            raise Exception("Error decoding content_details.json.")

    def generate(self, context):
        try:
            # Parse request data
            request = context["request"]
            data = json.loads(request["body"])
            theme = data.get("prompt")
            content_type = data.get("contentType")
            num_images = int(data.get("numImages", 1))
            platforms = data.get("platforms", {})

            if not theme or not content_type:
                return {"error": "Missing theme or content type."}, 400

            # ✅ STORE USER MANUAL PROMPT TO S3
            try:
                today = datetime.today().strftime('%Y-%m-%d')
                s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
                s3.put_object(
                    Bucket=os.getenv("S3_BUCKET_NAME"),
                    Key=f"user_prompts/{today}_prompt.txt",
                    Body=theme.encode('utf-8')
                )
                print(f"✅ Stored user-submitted prompt for {today}")
            except Exception as e:
                print(f"❌ Failed to store user prompt to S3: {str(e)}")

            # Step 1: Generate content_details.json
            self.run_content_generator(theme, num_images, content_type)

            # Step 2: Load content details
            content_details = self.load_content_details()
            subtopics = [
                {
                    "title": subtopic,
                    "slide_contents": content_details["slide_contents"].get(subtopic, []),
                    "captions": content_details["captions"].get(subtopic, [])
                }
                for subtopic in content_details["subtopics"]
            ]

            # Step 3: Transform subtopics to match the format expected by ImageGenerator
            transformed_subtopics = []
            for subtopic in subtopics:
                # Convert slide_contents to a string for "details"
                details = " ".join(subtopic["slide_contents"]) if subtopic["slide_contents"] else subtopic["title"]
                # Ensure captions is a list with at least one element
                captions = subtopic["captions"] if subtopic["captions"] else ["Default caption for " + subtopic["title"]]
                transformed_subtopic = {
                    "title": subtopic["title"],
                    "details": details,
                    "captions": captions
                }
                transformed_subtopics.append(transformed_subtopic)

            # Step 4: Generate images
            image_urls = self.image_generator.generate_images(theme, content_type, num_images, transformed_subtopics)

            # Step 5: Post to social media
            if platforms.get("instagram"):
                for image_url in image_urls:
                    post_image_to_instagram(image_url, "your_instagram_access_token", "your_ig_user_id")
            if platforms.get("x"):
                for image_url in image_urls:
                    post_image_to_twitter(
                        image_url,
                        "your_twitter_access_token",
                        "your_twitter_secret_token",
                        "your_twitter_consumer_key",
                        "your_twitter_consumer_secret"
                    )
            if platforms.get("linkedin"):
                for image_url in image_urls:
                    post_images_to_linkedin(image_url, "your_linkedin_access_token")

            return {"message": "Success", "image_urls": image_urls}

        except Exception as e:
            return {"error": str(e)}, 500
