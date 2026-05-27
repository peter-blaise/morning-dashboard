import anthropic
import re
from datetime import datetime

client = anthropic.Anthropic()

print("Fetching headlines...")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"""Today is {datetime.now().strftime('%B %d, %Y')}. 
Search for today's headlines from these outlets:
1. Wall Street Journal (wsj.com) - 7 headlines
2. NY Post (nypost.com) - 6 headlines  
3. TechCrunch (techcrunch.com) - 6 headlines
4. Financial Times (ft.com) - 6 headlines
5. The Economist (economist.com) - 5 headlines
6. The Information (theinformation.com) - 5 headlines
7. Stratechery (stratechery.com) - 4 headlines

Return ONLY a valid JSON array, no markdown, no explanation. Each object:
{{"source": "WSJ"|"NY Post"|"TechCrunch"|"FT"|"The Economist"|"The Information"|"Stratechery", "headline": "...", "url": "https://..."}}"""
    }]
)

# Extract text from response
text = ""
for block in message.content:
    if hasattr(block, "text"):
        text += block.text

# Parse JSON
match = re.search(r'\[[\s\S]*\]', text.replace('```json','').replace('```',''))
if not match:
    print("No JSON found in response")
    exit(1)

articles_json = match.group(0)

# Read current index.html
with open('index.html', 'r') as f:
    html = f.read()

# Replace ARTICLES array
new_articles = f"const ARTICLES = {articles_json};"
html = re.sub(r'const ARTICLES = \[[\s\S]*?\];', new_articles, html)

# Update last fetched date
today_str = datetime.now().strftime('%A, %B %d, %Y')
html = re.sub(
    r'Last fetched: .*? —',
    f'Last fetched: {today_str} —',
    html
)

with open('index.html', 'w') as f:
    f.write(html)

print(f"Done — updated index.html with fresh headlines for {today_str}")
