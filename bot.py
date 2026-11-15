import os
import feedparser
from google import genai

# Controleer of de API-sleutel aanwezig is
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY ontbreekt in de GitHub Secrets!")

client = genai.Client(api_key=api_key)

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:8]:
            title = getattr(entry, 'title', 'Geen titel')
            summary = getattr(entry, 'summary', '')
            items.append(f"- **{title}**: {summary}")
        return "\n".join(items)
    except Exception as e:
        print(f"Fout bij ophalen RSS van {url}: {e}")
        return ""

print("Bezig met ophalen van NOS en NU.nl RSS-feeds...")
nos_nieuws = fetch_rss("https://feeds.nos.nl/nosnieuwsalgemeen")
nu_nieuws = fetch_rss("https://www.nu.nl/rss/Algemeen")

totaal_nieuws = f"NOS Nieuws:\n{nos_nieuws}\n\nNU.nl Nieuws:\n{nu_nieuws}"

print("Bezig met genereren van de samenvatting via Gemini...")
response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents=f"Hier is het recente nieuws van vandaag:\n\n{totaal_nieuws}\n\nSelecteer de absolute top 3 belangrijkste nieuwsverhalen. Schrijf een heldere ochtendbriefing in het Nederlands met een pakkende titel en korte uitleg per verhaal. Geef schone HTML-code terug (alleen de inhoud binnen <div> of <section> tags, geen volledige html/head tags)."
)

html_content = response.text

pagina = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mijn Ochtendbriefing</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f7f9fa; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
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
