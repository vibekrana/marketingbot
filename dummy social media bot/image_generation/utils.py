import json
import re

# Define styles for different content types to guide image generation
content_type_styles = {
    "Informative": {
        "layouts": ["grid with icons", "flowchart", "annotated diagram"],
        "palette": "dark background with yellow highlights, white text",
        "font": "clean sans-serif font",
        "theme_adjustment": "Include meaningful explanatory visuals",
        "action": "Create an infographic-style image that explains"
    },
    "Inspirational": {
        "layouts": ["centered text with background image", "quote with border"],
        "palette": "black background with yellow text",
        "font": "bold decorative font",
        "theme_adjustment": "Use imagery that uplifts and aligns with the theme",
        "action": "Create an inspirational image about"
    },
    "Educational": {
        "layouts": ["step-by-step guide", "mind map"],
        "palette": "dark mode with yellow bullet points",
        "font": "educational readable font",
        "theme_adjustment": "Use educational icons and explanation cues",
        "action": "Create an educational image for"
    },
    "Promotional": {
        "layouts": ["product spotlight", "call-to-action banner"],
        "palette": "black background with yellow CTA, white content",
        "font": "bold marketing font",
        "theme_adjustment": "Showcase the theme with branding elements",
        "action": "Create a promotional image that promotes"
    }
}

def clean_text(text):
    """
    Remove special characters from text, keeping only alphanumeric characters and spaces.
    
    Args:
        text (str): The input text to clean.
    
    Returns:
        str: Cleaned text with only alphanumeric characters and spaces.
    """
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def get_content_details():
    """
    Load and parse content details from content_details.json.
    
    Returns:
        dict: A dictionary containing theme, number of subtopics, content type, and subtopics.
    
    Raises:
        FileNotFoundError: If content_details.json is not found.
        json.JSONDecodeError: If content_details.json cannot be decoded.
    """
    try:
        with open("content_details.json", "r") as f:
            content = json.load(f)
        return {
            "theme": content.get("theme", "Unknown Theme"),
            "num_subtopics": len(content.get("subtopics", [])),
            "content_type": content.get("content_type", "Educational"),
            "subtopics": [
                {
                    "title": subtopic,
                    "details": content["slide_contents"].get(subtopic, [subtopic.split(". ")[1] if ". " in subtopic else subtopic])[0],
                    "captions": content["captions"].get(subtopic, ["Default Caption"])
                }
                for subtopic in content.get("subtopics", [])
            ]
        }
    except FileNotFoundError:
        raise Exception("content_details.json not found.")
    except json.JSONDecodeError:
        raise Exception("Error decoding content_details.json.")