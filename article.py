from dataclasses import dataclass, field
from transformers import pipeline
import re
import torch


class Article:
    """Represents an article with its relevant chunks of text"""
    def __init__(self, title, link, chunks, requests_per_second=10):
        self.title = title
        self.link = link
        self.chunks = chunks
        self.sentiment_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0 if torch.cuda.is_available() else -1)

    def analyze_text(self, text: str) -> int:
        """Analyze the sentiment of a text chunk using LLM."""
        if not text:
            return 0
            
        try:
            # Clean the text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Get sentiment - ensure text is a list for batch processing
            label_to_score = {
                "very negative": -1.0,
                "negative": -0.5,
                "neutral": 0.0,
                "positive": 0.5,
                "very positive": 1.0
            }

            # Run the pipeline
            result = self.sentiment_pipeline(text, candidate_labels=list(label_to_score.keys()))

            # Calculate the weighted average score
            total_score = 0.0
            total_weight = 0.0

            for label, score in zip(result['labels'], result['scores']):  # type: ignore
                total_score += label_to_score[label] * score  # type: ignore
                total_weight += score

            # Final sentiment score if total_weight != 0: final_score = total_score / total_weight else: final_score = 0.0
            return total_score / total_weight if total_weight != 0 else 0  # type: ignore
            
        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return 0

    @property
    def sentiment_score(self):
        if not self.chunks:
            return 0
        chunk_sentiments = [self.analyze_text(chunk) for chunk in self.chunks]
        return sum(chunk_sentiments) / len(chunk_sentiments)
