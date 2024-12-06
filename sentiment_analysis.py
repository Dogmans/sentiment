from transformers import pipeline
import re
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt', quiet=True)

class SentimentAnalysis:
    def __init__(self):
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        self.max_length = 512  # Maximum token length for the model
        
    def chunk_text(self, text):
        """
        Intelligently chunk text into segments that respect sentence boundaries
        while staying under the max token length.
        """
        # First split into sentences
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            # Rough estimate of tokens (words + punctuation)
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length <= self.max_length:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def analyze_text(self, text):
        """
        Analyze sentiment of text, handling long texts by chunking and averaging.
        Returns a sentiment score between -1 and 1.
        """
        if not text or len(text.strip()) == 0:
            return 0
            
        try:
            # Clean the text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split into manageable chunks
            chunks = self.chunk_text(text)
            
            if not chunks:
                return 0
                
            # Analyze each chunk
            chunk_sentiments = []
            for chunk in chunks:
                result = self.sentiment_pipeline(chunk)[0]
                # Convert POSITIVE/NEGATIVE to numeric score
                score = result['score']
                if result['label'] == 'NEGATIVE':
                    score = -score
                chunk_sentiments.append(score)
            
            # Weight chunks by their length for final sentiment
            total_length = sum(len(chunk.split()) for chunk in chunks)
            weighted_sentiment = sum(
                sentiment * len(chunk.split()) / total_length
                for chunk, sentiment in zip(chunks, chunk_sentiments)
            )
            
            return weighted_sentiment
            
        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return 0

    def is_relevant(self, text, stock_data):
        """
        Check if the text is relevant to the stock using pattern matching first,
        then falling back to LLM-based relevance check if needed.
        """
        try:
            # First try exact match for efficiency
            pattern = f"\\b({re.escape(stock_data.symbol)}|{re.escape(stock_data.company_name)})\\b"
            if re.search(pattern, text, re.IGNORECASE):
                return True
            
            # If no exact match, use LLM for more sophisticated relevance checking
            # Create a prompt that includes both symbol and company name
            # Truncate text if too long to avoid token limit issues
            truncated_text = text[:1000] + "..." if len(text) > 1000 else text
            prompt = f"Is this text about {stock_data.company_name} ({stock_data.symbol})? Text: {truncated_text}"
            
            result = self.sentiment_pipeline(prompt)[0]
            return result['label'] == 'POSITIVE'
            
        except Exception as e:
            print(f"Error checking relevance: {str(e)}")
            return False

    def fetch_and_analyze(self, stock_data):
        """
        Fetch and analyze sentiment data for a stock.
        Returns list of (text, sentiment_score) tuples.
        """
        texts = self.fetch_data(stock_data)
        results = []
        
        for text in texts:
            if self.is_relevant(text, stock_data):
                sentiment = self.analyze_text(text)
                results.append((text, sentiment))
                
        return results

    def fetch_data(self, stock_data):
        """
        Abstract method to be implemented by subclasses.
        Should return a list of texts to analyze.
        """
        raise NotImplementedError("Subclasses must implement fetch_data")
