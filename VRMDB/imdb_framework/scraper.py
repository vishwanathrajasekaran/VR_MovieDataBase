# scraper.py
import time
import pandas as pd
from config import IMDB_ID_COLUMN
from data_io import read_input_csv, save_dataframe_csv
from pages.imdb_page import ImdbTitlePage
from imdb_Certification import imdb_certification

ACTIVE_FIELDS = {
    "Genre":         lambda page: page.get_genres(),
    "Languages":     lambda page: page.get_languages(),
    "Directors":     lambda page: page.get_directors(),
    "Writers":       lambda page: page.get_writers(),
    "Cast":          lambda page: page.get_cast(top_n=5),
    "Poster":        lambda page: page.get_poster_url(),
}

def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    col_values = {col: [] for col in ACTIVE_FIELDS.keys()}
    imdb_urls = []
    streaming_logos = []

    total = len(df)
    for idx, imdb_id in enumerate(df[IMDB_ID_COLUMN], start=1):
        imdb_id = str(imdb_id).strip()
        print(f"Processing {idx}/{total}: {imdb_id}")

        page = ImdbTitlePage(imdb_id)
        imdb_urls.append(page.url)

        # POM methods using requests/BS4
        for col_name, getter in ACTIVE_FIELDS.items():
            value = getter(page)
            col_values[col_name].append(value)

        # POM method using Selenium for streaming logo
        logo_url = page.get_streaming_logo_url()
        streaming_logos.append(logo_url)

        print(
            f"| StreamingLogo: {logo_url} "
            f"| Languages: {col_values['Languages'][-1]} "
            f"| Directors: {col_values['Directors'][-1]}"

        )

        time.sleep(1)

    df["IMDB URL"] = imdb_urls
    for col_name, values in col_values.items():
        df[col_name] = values
    df["StreamingLogo"] = streaming_logos

    return df

def run_enrichment() -> str:
    df = read_input_excel()
    enriched = enrich_dataframe(df)
    path = save_enriched_excel(enriched)
   
    return path
