from dataclasses import dataclass
from typing import List

@dataclass
class Article:
    """Represents an article with its relevant chunks of text"""
    title: str
    url: str
    chunks: List[str]
    sentiment_analyzer: 'SentimentAnalysis'

    @property
    def sentiment_score(self):
        if not self.chunks:
            return 0
        chunk_sentiments = [self.sentiment_analyzer.analyze_text(chunk) for chunk in self.chunks]
        return sum(chunk_sentiments) / len(chunk_sentiments)

# Avoid circular import
from sentiment_analysis import SentimentAnalysis
