import os
import sqlite3
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_url(session, url, cookies, banned_profiles):
    async with session.get(url, cookies=cookies) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')
        title = soup.title.string.strip()
        if title == "Instagram":
            print(f"The {url} profile does not exist.")
            banned_profiles.append(url.split('/')[-2])  # Extract username from URL

async def main():
    cookie_file = os.path.expanduser('~') + '\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\dul21l1q.default-release\\cookies.sqlite'
    conn = sqlite3.connect(cookie_file)
    cursor = conn.cursor()
    
    cursor.execute('SELECT name, value FROM moz_cookies')
    cookies = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()

    with open('is_verified.json', 'r') as f:
        data = json.load(f)
        usernames = data

    urls = [f"https://www.instagram.com/{username}/" for username in usernames]

    banned_profiles = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url, cookies, banned_profiles) for url in urls]
        await asyncio.gather(*tasks)

    with open('is_banned.json', 'w') as f:
        json.dump(banned_profiles, f)

asyncio.run(main())
