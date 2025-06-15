class CaptionFilter:
    @staticmethod
    def filter_captions(captions, max_length=50, keywords=None):
        if keywords is None:
            keywords = []
        filtered = []
        for caption in captions:
            if len(caption) <= max_length and all(keyword.lower() in caption.lower() for keyword in keywords):
                filtered.append(caption)
        return filtered[:3]  # Return top 3 filtered captions

if __name__ == "__main__":
    captions = ["AI boosts marketing ROI!", "Learn AI marketing today!", "AI is the future of ads (long text)"]
    filtered = CaptionFilter.filter_captions(captions, keywords=["AI", "marketing"])
    print(filtered)