import os
import json
import time
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai  # Ensure this import is present

try:
    from content_handler import ContentHandler as ContentGenerator
except ImportError:
    from content_handler import ContentGenerator  # fallback for older naming

# Load environment variables
load_dotenv()

# Configs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
S3_PROMPT_KEY_PREFIX = "user_prompts"

# Clients
client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Ensure the openai client is initialized here
s3 = boto3.client("s3", region_name=AWS_REGION)

# Function to delete yesterday's prompt from S3
def delete_yesterday_prompt():
    tz = pytz.timezone("Asia/Kolkata")
    yesterday = (datetime.now(tz) - timedelta(days=1)).strftime('%Y-%m-%d')
    prompt_key = f"{S3_PROMPT_KEY_PREFIX}/{yesterday}_prompt.txt"
    try:
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=prompt_key)
        print(f"🗑️ Deleted yesterday's prompt: {prompt_key}")
    except s3.exceptions.NoSuchKey:
        print(f"✅ No prompt to delete for {yesterday} (key not found).")
    except Exception as e:
        print(f"❌ Error deleting prompt for {yesterday}: {e}")

# Selenium setup function using the Chrome profile path from environment variable
def setup_selenium_driver():
    options = Options()
    
    # Fetch the Chrome profile path from environment variables
    chrome_profile_path = os.getenv('CHROME_PROFILE_PATH')
    
    if not chrome_profile_path:
        raise ValueError("Chrome profile path not found in environment variables.")
    
    # Setting the user data dir to use the specific Chrome profile
    options.add_argument(f"user-data-dir={chrome_profile_path}")
    
    # Disable automation flag to prevent detection of Selenium
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Open Chrome maximized
    options.add_argument("--start-maximized")
    
    # Initialize the driver with the options
    driver = webdriver.Chrome(options=options)
    
    return driver

# Fetch trending topics from ChatGPT
def fetch_trending_from_chatgpt():
    driver = setup_selenium_driver()
    driver.get("https://chat.openai.com/")
    
    try:
        # Wait for the page to fully load and for the input field to be present
        input_field = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='prompt-textarea']/p"))
        )
        
        # Send the updated prompt to ChatGPT
        input_field.send_keys("Non-sensitive trending topics in India for today in line by line")
        input_field.send_keys(Keys.RETURN)
        
        # Wait for the response from ChatGPT
        time.sleep(20)  # Allow more time for response generation
        
        # Extract the response from ChatGPT
        messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message-text')]")
        
        # Print the page source to help debug the issue
        print("Page Source:", driver.page_source)  # This will help debug the issue
        
        # If messages are found, get the latest one
        if messages:
            response_text = messages[-1].text
            print("ChatGPT Response:", response_text)  # Debugging print
        else:
            response_text = "No response found."
            print("No messages found.")
        
        driver.quit()  # Close the browser once done
        return response_text.strip()
    
    except Exception as e:
        print(f"Error while fetching trending topics from ChatGPT: {e}")
        driver.quit()  # Ensure that the browser is closed if an error occurs
        return ""

# Function to choose the best trending topic related to Data Science or AI
def choose_best_topic(response):
    # Split the response into topics (line by line)
    topics = response.split("\n")
    selected_topic = ""
    
    # Loop through the topics and select the one related to Data Science or AI
    for topic in topics:
        if "data" in topic.lower() or "ai" in topic.lower():
            selected_topic = topic
            break
    
    # If no relevant topic found, pick a generic topic related to GenAI
    if not selected_topic:
        selected_topic = "Explore the future of GenAI and its role in data science."

    return selected_topic

# Generate a molded prompt based on the selected topic
def generate_molded_prompt(selected_topic):
    return f"Explore how '{selected_topic}' influences AI and machine learning trends."

# Function to check if a user prompt already exists for today in the S3 bucket
def check_user_prompt_for_today():
    today = datetime.today().strftime('%Y-%m-%d')
    prompt_key = f"{S3_PROMPT_KEY_PREFIX}/{today}_prompt.txt"
    try:
        s3_response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=prompt_key)
        user_prompt = s3_response['Body'].read().decode('utf-8')
        print(f"User prompt found for today: {user_prompt}")
        return user_prompt
    except s3.exceptions.NoSuchKey:
        print("No prompt found for today.")
        return None
    except Exception as e:
        print(f"Error checking for user prompt: {e}")
        return None

# Store the generated prompt in S3
def store_prompt_in_s3(prompt):
    today = datetime.today().strftime('%Y-%m-%d')
    prompt_key = f"{S3_PROMPT_KEY_PREFIX}/{today}_prompt.txt"
    try:
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=prompt_key, Body=prompt.encode('utf-8'))
        print(f"Prompt stored in S3 with key: {prompt_key}")
    except Exception as e:
        print(f"Error storing prompt in S3: {e}")

# Scheduler task for daily execution
def scheduler_task():
    print("Scheduler task started...")
    user_prompt = check_user_prompt_for_today()
    if user_prompt:
        print("Skipping prompt generation as the user has submitted a prompt for today.")
        return

    # Fetch trending topics from ChatGPT
    trending_response = fetch_trending_from_chatgpt()
    print(f"ChatGPT response: {trending_response}")
    
    # Choose the best topic from the response
    selected_topic = choose_best_topic(trending_response)
    print(f"Selected Topic: {selected_topic}")
    
    # Generate a molded prompt based on the selected topic
    molded_prompt = generate_molded_prompt(selected_topic)
    print(f"Generated Molded Prompt: {molded_prompt}")
    
    # Store the generated prompt in S3
    store_prompt_in_s3(molded_prompt)

    # Generate image URLs using the molded prompt
    content_generator = ContentGenerator()
    image_urls = content_generator.generate({
        "request": {
            "body": json.dumps({
                "prompt": molded_prompt,
                "contentType": "Informative",
                "numImages": 1,
                "platforms": {
                    "instagram": True,
                    "x": True,
                    "linkedin": True
                }
            })
        }
    })

    print(f"Generated Image URLs: {image_urls}")

# Function to run the scheduler periodically
def run_scheduler():
    schedule.every().day.at("00:00").do(delete_yesterday_prompt)
    schedule.every().day.at("09:13").do(scheduler_task)  # 🔁 updated for testing
    print("✅ Scheduler loop is running...")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
