import httpx
import asyncio
import re
import winsound
from datetime import datetime
from termcolor import cprint
from twikit import Client, TooManyRequests

# Setup for Twikit
client = Client(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')

# Load previously saved cookies for authentication
client.load_cookies("cookies.json")

# Define search parameters
search_queries = ["pump.fun/", "pump", "wallet"]
pump_fun_pattern = re.compile(r"pump\.fun/.*")  # Regex pattern to match "pump.fun/*"
solana_address_pattern = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")  # Solana address pattern
min_followers = 10000  # Minimum followers required
ignore_list = set()  # Track processed tweet IDs

async def search_and_filter_tweets():
    try:
        filtered_tweets = []
        
        for query in search_queries:
            # Search for tweets containing each query
            tweets = await client.search_tweet(query, product="Latest")
            
            for tweet in tweets:
                if tweet.id in ignore_list:
                    continue
                user = tweet.user
                if user.is_blue_verified and user.followers_count >= min_followers:
                    expanded_urls = [
                        url['expanded_url'] for url in tweet.urls
                        if url.get('expanded_url') and pump_fun_pattern.search(url['expanded_url'])
                    ]
                    # Check if tweet text or URLs contain a Solana address
                    solana_addresses = solana_address_pattern.findall(tweet.text)
                    
                    if expanded_urls or solana_addresses:
                        filtered_tweets.append({
                            'tweet_id': tweet.id,
                            'username': user.screen_name,
                            'followers': user.followers_count,
                            'verified': user.is_blue_verified,
                            'text': tweet.text,
                            'expanded_urls': expanded_urls,
                            'solana_addresses': solana_addresses,
                            'timestamp': tweet.created_at
                        })
                        ignore_list.add(tweet.id)
                        for url in expanded_urls:
                            CA = url.replace("https://pump.fun/", "")

        # Display and play sound for each filtered tweet
        for tweet in filtered_tweets:
            cprint(f"User: @{tweet['username']} , Followers: {tweet['followers']}", "green", attrs=["bold"])
            cprint(f"Link: https://x.com/{tweet['username']}/status/{tweet['tweet_id']}", "white" )
            cprint(f"Tweet:\n{tweet['text']}\n", "white")
            if tweet['expanded_urls']:
                cprint(f"PUMP LINK: https://pump.fun/{CA}\n", "blue")
            
            # If Solana addresses found, display them
            if tweet['solana_addresses']:
                cprint(f"Solana Addresses: {', '.join(tweet['solana_addresses'])}\n", "magenta")
            
            # Play alert sound
            try:
                winsound.PlaySound("alert.wav", winsound.SND_FILENAME)
            except Exception as e:
                print(f"Failed to play sound: {e}")

        return filtered_tweets

    except TooManyRequests as e:
        reset_time = datetime.fromtimestamp(e.rate_limit_reset)
        print(f"Rate limit reached. Will reset at {reset_time}.")
        wait_time = (reset_time - datetime.now()).total_seconds()
        await asyncio.sleep(wait_time)
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the search asynchronously every 30 seconds
async def main_loop():
    while True:
        print(f"Searching..................")
        await search_and_filter_tweets()
        await asyncio.sleep(50)  # Wait for 30 seconds before the next iteration

# Run the main loop function
if __name__ == "__main__":
    asyncio.run(main_loop())
