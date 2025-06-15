import json
import argparse
from openai import OpenAI
from config import OPENAI_API_KEY
from prompt_templates import PromptTemplates

client = OpenAI(api_key=OPENAI_API_KEY)

class ContentGenerator:
    def __init__(self):
        self.client = client

    def generate_subtopic_options(self, theme, num, content_type):
        prompt_map = {
            "Informative": f"Deliver 3 *completely distinct*, razor-sharp, educational subtopic options for #{num} on '{theme}'. Cover *only* definition, types, applications, history, or future, using a), b), c), each under 12 words, **bold key phrase**, vivid, image-ready text. No repeats, no overlap, no filler!",
            "Inspirational": f"Unleash 3 *completely distinct*, bold, uplifting subtopic options for #{num} on '{theme}'. Cover *only* definition, types, applications, history, or future, using a), b), c), each under 12 words, **bold key phrase**, inspiring, image-perfect. No repeats, no overlap, skip extras!",
            "Promotional": f"Fire up 3 *completely distinct*, dynamic, sales-driven subtopic options for #{num} on '{theme}'. Cover *only* definition, types, applications, history, or future, using a), b), c), each under 12 words, **bold key phrase**, catchy, image-optimized. No repeats, no overlap, no fluff!",
            "Educational": f"Craft 3 *completely distinct*, brilliant, teaching-focused subtopic options for #{num} on '{theme}'. Cover *only* definition, types, applications, history, or future, using a), b), c), each under 12 words, **bold key phrase**, clear, image-friendly. No repeats, no overlap, no waste!"
        }
        prompt = prompt_map.get(content_type, prompt_map["Educational"])

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        content = response.choices[0].message.content
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        options = []
        for line in lines:
            if line.startswith(("a)", "b)", "c)")):
                options.append(line)
        if not options:
            print(f"Warning: No valid options found for subtopic {num}. Full response: {content}")
        print(f"Generated options for #{num}: {options}")
        return options[:3]

    def select_best_subtopic(self, options):
        if not options:
            return ""
        return min(options, key=len)

    def ensure_unique_subtopics(self, theme, content_type, target_count):
        unique_subtopics = []
        max_attempts = 10
        attempt = 0

        while len(unique_subtopics) < target_count and attempt < max_attempts:
            new_options = self.generate_subtopic_options(theme, len(unique_subtopics) + 1, content_type)
            for option in new_options:
                if option and option not in unique_subtopics:
                    unique_subtopics.append(option)
                if len(unique_subtopics) >= target_count:
                    break
            attempt += 1
        if len(unique_subtopics) < target_count:
            print(f"Warning: Could only generate {len(unique_subtopics)} unique subtopics after {max_attempts} attempts. Full list: {unique_subtopics}")
        return unique_subtopics[:target_count]

    def generate_slide_content(self, subtopic, content_type):
        prompt_map = {
            "Informative": f"Deliver razor-sharp slide content for '{subtopic}'. Title (bold), 1-2 lines, under 15 words, fact-rich, image-ready. No filler!",
            "Inspirational": f"Unleash bold, uplifting slide content for '{subtopic}'. Title (bold), 1-2 lines, under 15 words, motivating, image-perfect. Skip extras!",
            "Promotional": f"Fire up dynamic, sales-driven slide content for '{subtopic}'. Title (bold), 1-2 lines, under 15 words, catchy, image-optimized. No fluff!",
            "Educational": f"Craft brilliant, teaching-focused slide content for '{subtopic}'. Title (bold), 1-2 lines, under 15 words, clear, image-friendly. No waste!"
        }
        prompt = prompt_map.get(content_type, prompt_map["Educational"])

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        content = response.choices[0].message.content
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        slide_content = []
        for line in lines:
            if line and not line.startswith("Sure!") and not line.startswith("Certainly!"):
                slide_content.append(line)
        return slide_content[:2]

    def generate_captions(self, subtopic, content_type):
        style_map = {
            "Informative": "Forge 3 crisp, fact-packed captions for: [subtopic]. Under 10 words, #hashtag, emoji, image-savvy, no fluff.",
            "Inspirational": "Ignite 3 soul-stirring captions for: [subtopic]. Under 10 words, #hashtag, emoji, visually bold, pure vibe.",
            "Promotional": "Blast 3 irresistible, sales-boosting captions for: [subtopic]. Under 10 words, #hashtag, emoji, eye-catching, action-driven.",
            "Educational": "Shape 3 sharp, mind-opening captions for: [subtopic]. Under 10 words, #hashtag, emoji, clear, image-popping."
        }
        prompt = style_map.get(content_type, style_map["Educational"]).replace("[subtopic]", subtopic)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return [line.strip() for line in response.choices[0].message.content.split("\n") if line.strip()][:3]

    def generate_summary(self, subtopics, captions, content_type):
        style_map = {
            "Informative": "Distill [subtopics] and [captions] into 3 tight, fact-rich summary lines. Under 15 words each, image-friendly, no excess.",
            "Inspirational": "Transform [subtopics] and [captions] into 3 uplifting summary lines. Under 15 words each, motivational, image-ready, pure energy.",
            "Promotional": "Synthesize [subtopics] and [captions] into 3 punchy summary lines with a call to action. Under 15 words each, image-optimized, sell it!",
            "Educational": "Condense [subtopics] and [captions] into 3 clear, teaching summary lines. Under 15 words each, image-perfect, insightful."
        }
        prompt = style_map.get(content_type, style_map["Educational"]).replace("[subtopics]", str(subtopics)).replace("[captions]", str(captions))
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return [line.strip() for line in response.choices[0].message.content.split("\n") if line.strip()][:3]

    def generate_content(self, theme, num_subtopics, content_type):
        subtopics = self.ensure_unique_subtopics(theme, content_type, num_subtopics)
        subtopics = [f"{i}. {subtopic}" for i, subtopic in enumerate(subtopics, 1)]
        print(f"Selected subtopics: {[s.split('. ')[1] for s in subtopics]}")
        slide_contents = {subtopic: self.generate_slide_content(subtopic.split(". ")[1], content_type) for subtopic in subtopics}
        captions_dict = {subtopic: self.generate_captions(subtopic.split(". ")[1], content_type) for subtopic in subtopics}
        summary = self.generate_summary([subtopic.split(". ")[1] for subtopic in subtopics], 
                                      [cap for caps in captions_dict.values() for cap in caps], content_type)
        content = {
            "subtopics": subtopics,
            "slide_contents": slide_contents,
            "captions": captions_dict,
            "summary": summary
        }
        # Save to content_details.json
        with open("content_details.json", "w") as f:
            json.dump(content, f, indent=4)
        return content

    def print_clean_output(self, theme, num_subtopics, content_type, content):
        print(f"\n**Theme: {theme}** (Content Type: {content_type}, Subtopics: {num_subtopics})\n")
        print("#### Subtopics (Slide Titles)")
        for i, subtopic in enumerate(content["subtopics"], 1):
            print(f"{i}. {subtopic.split('. ')[1]}")
        print("\n#### Slide Content")
        for subtopic, content_lines in content["slide_contents"].items():
            title = subtopic.split(". ")[1]
            print(f"- **{title}**:")
            for line in content_lines:
                if line:
                    print(f"  - {line}")
        print("\n#### Captions")
        for subtopic, captions in content["captions"].items():
            print(f"- **For {subtopic.split('. ')[1]}**:")
            for caption in captions:
                if caption:
                    print(f"  - {caption}")
        print("\n#### Summary")
        for line in content["summary"]:
            print(f"- {line}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate content for a given theme.")
    parser.add_argument("--theme", type=str, required=True, help="Theme for content generation")
    parser.add_argument("--num_subtopics", type=int, required=True, help="Number of subtopics/images (1-5)")
    parser.add_argument("--content_type", type=str, required=True, help="Content type (Informative, Inspirational, Promotional, Educational)")
    args = parser.parse_args()

    theme = args.theme
    num_subtopics = max(1, min(5, args.num_subtopics))
    content_type = args.content_type.capitalize()

    generator = ContentGenerator()
    content = generator.generate_content(theme, num_subtopics, content_type)
    generator.print_clean_output(theme, num_subtopics, content_type, content)