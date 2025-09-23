from datetime import datetime

import requests

URL = "https://gnews.io/api/v4/"


def format_request_output(response: requests.Response) -> str:
    """Format the API response into a readable string."""

    def format_date(date_str):
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%b %d, %Y %H:%M")
        except Exception:
            return date_str

    articles = response.json().get("articles", [])
    return ("\n" + "-" * 10 + "\n").join(
        f"**{article['title']}** ({article['source']['name']}, {format_date(article['publishedAt'])})\n{article['description']}\n{article['content']}"
        for article in articles
    ) or "No articles found."


def top_headlines(api_key: str, category: str | None = None):
    """Fetch top headlines. Optionally filter by category."""
    valid_categories = [
        "general",
        "world",
        "nation",
        "business",
        "technology",
        "entertainment",
        "sports",
        "science",
        "health",
    ]
    if category and category not in valid_categories:
        raise ValueError(
            "Invalid category. Choose from: " + ", ".join(valid_categories)
        )

    response = requests.get(
        f"{URL}top-headlines",
        params={"country": "us", "lang": "en", "category": category, "apikey": api_key},
    )

    return format_request_output(response)


def webquery(query: str, api_key: str):
    """Search for articles based on a query string."""
    response = requests.get(
        f"{URL}search",
        params={
            "q": query,
            "sortby": "relevance",
            "lang": "en",
            "max": 10,
            "apikey": api_key,
        },
    )

    return format_request_output(response)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv(".env")
    api_key = os.getenv("GNEWS_API_KEY")

    if not api_key:
        raise ValueError("GNEWS_API_KEY not found in environment variables.")

    print("Top Headlines:")
    headlines = top_headlines(api_key, category="technology")
    print(headlines)

    print("\nSearch Results for 'AI':")
    search_results = webquery("AI", api_key)
    print(search_results)
