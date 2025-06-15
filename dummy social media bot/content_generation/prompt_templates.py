class PromptTemplates:
    @staticmethod
    def get_subtopics_prompt(theme):
        return f"Give 5 subtopics for the theme: {theme}"

    @staticmethod
    def get_captions_prompt(subtopic):
        return f"Generate 3 catchy captions for: {subtopic}"

    @staticmethod
    def get_summary_prompt(subtopics, captions):
        return f"Summarize all subtopics {subtopics} and captions {captions} into a 3-line overview"