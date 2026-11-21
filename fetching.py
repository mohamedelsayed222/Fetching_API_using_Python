import os
import sys
import textwrap
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from the same folder as this script
load_dotenv(Path(__file__).parent / ".env")

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.nasa.gov/planetary/apod"


class SpaceEntry:
    """Stores and organizes one Astronomy Picture of the Day entry."""

    def __init__(self, title, date, media_type, url, explanation, copyright_=None):
        self.title = title
        self.date = date
        self.media_type = media_type
        self.url = url
        self.explanation = explanation
        self.copyright = copyright_ or "Public domain / NASA"

    @classmethod
    def from_json(cls, data):
        """Build a SpaceEntry from the parsed JSON response."""
        return cls(
            title=data["title"],
            date=data["date"],
            media_type=data["media_type"],
            url=data["url"],
            explanation=data["explanation"],
            copyright_=data.get("copyright", "").strip() or None,
        )

    def summary(self):
        line = "=" * 60
        wrapped = textwrap.fill(self.explanation, width=58)
        return (
            f"{line}\n"
            f" NASA Astronomy Picture of the Day\n"
            f"{line}\n"
            f" Title     : {self.title}\n"
            f" Date      : {self.date}\n"
            f" Media type: {self.media_type}\n"
            f" Credit    : {self.copyright}\n"
            f" Link      : {self.url}\n"
            f"{line}\n"
            f" About:\n{textwrap.indent(wrapped, ' ')}\n"
            f"{line}"
        )


def fetch_apod(date=None):
    params = {"api_key": API_KEY}
    if date:
        params["date"] = date  # format: YYYY-MM-DD
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()  # JSON parsing


def main():
    if not API_KEY:
        sys.exit("Error: API_KEY not found. Add it to your .env file.")

    date = input("Enter a date (YYYY-MM-DD) or press Enter for today: ").strip()

    try:
        data = fetch_apod(date or None)
        entry = SpaceEntry.from_json(data)
        print(entry.summary())
    except requests.exceptions.HTTPError as e:
        # Print only the status code so the key never appears in output
        print(f"API error: HTTP {e.response.status_code}")
    except requests.exceptions.RequestException:
        print("Network error: could not reach the NASA API.")
    except (KeyError, ValueError):
        print("Unexpected response format.")


if __name__ == "__main__":
    main()