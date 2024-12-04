# Financial Sentiment Analysis Bot

A Python-based bot that analyzes sentiment across multiple financial news and social media platforms.

## Setup

1. Install required dependencies: 

```
pip install -r requirements.txt
```     

2. Set up API credentials for platforms:
   - [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
   - [Reddit Apps](https://www.reddit.com/prefs/apps)
   - No API credentials needed for Motley Fool and MSN Money

3. Configure your credentials in the project

## Features
- Multi-platform Sentiment Analysis:
  - Twitter sentiment analysis
  - Reddit discussions analysis
  - Motley Fool articles analysis
  - MSN Money news analysis
- Stock symbol tracking
- Sentiment scoring
- Cross-platform comparison

## Configuration
1. Create a `.env` file in the root directory
2. Add your API credentials:

```
# Twitter
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Reddit
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

## Usage
Run the sentiment analysis:

```
python main.py
```

## Supported Platforms
- Twitter: Social media sentiment analysis
- Reddit: Community discussion sentiment
- Motley Fool: Financial news analysis
- MSN Money: Market news sentiment

## Project Structure
```
├── main.py                   # Main script
├── requirements.txt          # Required packages
├── sentiment_analysis.py     # Sentiment analysis implementations
├── .env                      # Environment variables (not in git)
└── README.md                 # Documentation
```

## Output Format
For each platform and stock symbol, the bot outputs:
- Text content analyzed
- Sentiment score