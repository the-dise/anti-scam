import os  # For interacting with the operating system
import sqlite3  # For SQLite database operations
import json  # For handling JSON data
import asyncio  # For asynchronous programming
import aiohttp  # For asynchronous HTTP requests
from bs4 import BeautifulSoup  # For HTML parsing

# Asynchronous function to fetch URL content
async def fetch_url(session, url, cookies, banned_profiles):
    # Asynchronously get the URL content
    async with session.get(url, cookies=cookies) as response:
        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(await response.text(), 'lxml')
        # Extract the title of the webpage
        title = soup.title.string.strip()
        # Check if the title indicates a non-existent profile
        if title == "Instagram":
            # Print a message indicating that the profile does not exist
            print(f"The {url} profile does not exist.")
            # Append the profile URL to the list of banned profiles
            banned_profiles.append(url.split('/')[-2])

# Asynchronous main function
async def main():
    # Path to Firefox cookies database
    cookie_file = os.path.expanduser('~') + '\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\dul21l1q.default-release\\cookies.sqlite'
    # Connect to the cookies database
    conn = sqlite3.connect(cookie_file)
    cursor = conn.cursor()
    
    # Select cookies data from the database
    cursor.execute('SELECT name, value FROM moz_cookies')
    # Create a dictionary of cookies
    cookies = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Close the database connection
    conn.close()

    # Read usernames from a JSON file
    with open('is_verified.json', 'r') as f:
        data = json.load(f)
        usernames = data

    # Generate list of profile URLs
    urls = [f"https://www.instagram.com/{username}/" for username in usernames]

    # List to store banned profiles
    banned_profiles = []

    # Asynchronously create a session for making HTTP requests
    async with aiohttp.ClientSession() as session:
        # Create tasks to fetch URL content asynchronously
        tasks = [fetch_url(session, url, cookies, banned_profiles) for url in urls]
        # Gather and wait for all tasks to complete
        await asyncio.gather(*tasks)

    # Write list of banned profiles to a JSON file
    with open('is_banned.json', 'w') as f:
        json.dump(banned_profiles, f)

# Run the main function asynchronously
asyncio.run(main())
