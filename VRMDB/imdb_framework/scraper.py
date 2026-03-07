# scraper.py

import time
import pandas as pd
from config import IMDB_ID_COLUMN
from pages.imdb_page import ImdbTitlePage

ACTIVE_FIELDS = {
    "Genre": lambda page: page.get_genres(),
    "Languages": lambda page: page.get_languages(),
    "Directors": lambda page: page.get_directors(),
    "Writers": lambda page: page.get_writers(),
    "Cast": lambda page: page.get_cast(top_n=5),
    "Poster": lambda page: page.get_poster_url(),
    "Plot": lambda page: page.get_plot_summary(),
}

def enrich_dataframe(df: pd.DataFrame, driver) -> pd.DataFrame:

    col_values = {col: [] for col in ACTIVE_FIELDS.keys()}
    imdb_urls = []
    streaming_logos = []

    total = len(df)

    for idx, imdb_id in enumerate(df[IMDB_ID_COLUMN], start=1):

        imdb_id = str(imdb_id).strip()

        print(f"\nProcessing {idx}/{total}: {imdb_id}")

        page = ImdbTitlePage(imdb_id, driver)

        imdb_urls.append(page.url)

        # Navigate to page once
        page.fetch()

        # Extract page fields
        for col_name, getter in ACTIVE_FIELDS.items():

            try:
                value = getter(page)
            except Exception as e:
                print(f"[ERROR] {col_name} failed for {imdb_id}: {e}")
                value = ""

            col_values[col_name].append(value)

        # Streaming logos (Selenium based)
        try:
            logo_url = page.get_streaming_logo_url()
        except Exception as e:
            print(f"[ERROR] Streaming logo failed for {imdb_id}: {e}")
            logo_url = ""

        streaming_logos.append(logo_url)

        print(
            f"| StreamingLogo: {logo_url} "
            f"| Languages: {col_values['Languages'][-1]} "
            f"| Directors: {col_values['Directors'][-1]}"
        )

        time.sleep(1)

    # Add results to dataframe
    df["IMDB URL"] = imdb_urls

    for col_name, values in col_values.items():
        df[col_name] = values

    df["StreamingLogo"] = streaming_logos

    return df