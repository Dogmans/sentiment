import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def fetch_clinical_trials_rss():
    url = 'https://clinicaltrials.gov/ct2/results/rss.xml?lup_s=30&lup_e=60'  # RSS feed for trials updated in the last 30 days
    response = requests.get(url)
    return response.content

def parse_rss(feed_content):
    root = ET.fromstring(feed_content)
    items = []
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        pub_date = item.find('pubDate').text
        items.append({'title': title, 'link': link, 'pubDate': pub_date})
    return items

def filter_upcoming_trials(trials, days_until_conclusion=30):
    filtered_trials = []
    now = datetime.now()
    for trial in trials:
        pub_date = datetime.strptime(trial['pubDate'], '%a, %d %b %Y %H:%M:%S %Z')
        if now <= pub_date <= now + timedelta(days=days_until_conclusion):
            filtered_trials.append(trial)
    return filtered_trials

def main():
    rss_content = fetch_clinical_trials_rss()
    trials = parse_rss(rss_content)
    upcoming_trials = filter_upcoming_trials(trials, days_until_conclusion=30)
    
    for trial in upcoming_trials:
        print(f"Title: {trial['title']}")
        print(f"Link: {trial['link']}")
        print(f"Publication Date: {trial['pubDate']}")
        print()

if __name__ == "__main__":
    main()
