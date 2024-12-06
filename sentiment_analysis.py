from transformers import pipeline

class SentimentAnalysis:
    def __init__(self):
        self.sentiment_model = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

    def fetch_and_analyze(self, query, count=100):
        data = self.fetch_data(query, count)
        sentiments = []
        for text in data:
            analysis = self.sentiment_model(text[:512])  # Truncate to max length
            sentiments.append((text, 1 if analysis[0]['label'] == 'POSITIVE' else -1))
        return sentiments

    def fetch_data(self, query, count):
        raise NotImplementedError("Subclasses should implement this method")
