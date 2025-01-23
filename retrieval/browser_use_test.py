from browser_use import Agent
from langchain_huggingface import ChatHuggingFace

# Load the model from Hugging Face
llm = HuggingFaceLLM(model="gpt2")

'''
https://python.langchain.com/docs/integrations/chat/huggingface/
'''

def search_marketwatch_articles(ticker_symbol):
    agent = Agent(
        task=f"Go to MarketWatch.com, search for articles about {ticker_symbol} published in the last day, and return the titles.",
        llm=llm
    )
    result = agent.run()
    return result

def main():
    ticker_symbol = "NFLX"  # Example ticker symbol for Netflix
    articles = search_marketwatch_articles(ticker_symbol)
    print(f"Articles about {ticker_symbol} published in the last day:")
    for article in articles:
        print(article)

if __name__ == "__main__":
    main()
