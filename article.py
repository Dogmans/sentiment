from dataclasses import dataclass, field
from typing import List
from transformers import pipeline
import re
import torch

@dataclass
class Article:
    """Represents an article with its relevant chunks of text"""
    title: str
    url: str
    chunks: List[str]
    sentiment_pipeline: pipeline = field(default_factory=lambda: pipeline("sentiment-analysis", device=0 if torch.cuda.is_available() else -1))

    def analyze_text(self, text: str) -> int:
        """Analyze the sentiment of a text chunk using LLM."""
        if not text:
            return 0
            
        try:
            # Clean the text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Get sentiment - ensure text is a list for batch processing
            results = self.sentiment_pipeline([text])
            if not results:
                return 0
            result = results[0]
            return 1 if result['label'] == 'POSITIVE' else -1
            
        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return 0

    @property
    def sentiment_score(self):
        if not self.chunks:
            return 0
        chunk_sentiments = [self.analyze_text(chunk) for chunk in self.chunks]
        return sum(chunk_sentiments) / len(chunk_sentiments)
