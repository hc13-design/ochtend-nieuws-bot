import os
import feedparser
from google import genai

# Initialiseer de Gemini API met je geheime sleutel
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def fetch_rss(url):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:10]: # Neem de laatste 10 van elke bron
        items.append(f"- **{entry.title}**: {getattr(entry, 'summary', '')}")
    return "\n".join(items)

# Haal nieuws op
print("Nieuws ophalen...")
nos_nieuws = fetch_rss("https://feeds.nos.nl/nosnieuwsalgemeen")
nu_nieuws = fetch_rss("https://www.nu.nl/rss/Algemeen")

totaal_nieuws = f"NOS Nieuws:\n{nos_nieuws}\n\nNU.nl Nieuws:\n{nu_nieuws}"

# Vraag Gemini om de top 3 samenvatting
print("Bezig met samenvatten via AI...")
response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents=f"Hier is het recente nieuws van vandaag:\n\n{totaal_nieuws}\n\nSelecteer de absolute top 3 belangrijkste of meest interessante nieuwsverhalen van dit moment. Schrijf een heldere, frisse ochtendbriefing in het Nederlands voor elk van de 3 verhalen met een pakkende titel en een korte uitleg. Geef het terug in schone HTML-code (alleen de inhoud binnen <div> of <section> tags, geen volledige html/head tags nodig, wel mooie opmaak met koppen en paragrafen)."
)

html_content = response.text

# Maak een volledige index.html pagina aan
pagina = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mijn Ochtendbriefing</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f7f9fa; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #111; font-size: 24px; border-bottom: 2px solid #eaeaea; padding-bottom: 10px; }}
        .news-card {{ background: white; padding: 16px; margin-bottom: 16px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .footer {{ text-align: center; font-size: 12px; color: #888; margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>☀️ Jouw Ochtendbriefing</h1>
    <div class="news-card">
        {html_content}
    </div>
    <div class="footer">Automatisch gegenereerd door jouw AI-bot</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(pagina)

print("index.html succesvol aangemaakt!")
