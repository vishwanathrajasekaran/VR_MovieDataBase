# scraper.py

import time
import pandas as pd
from bs4 import BeautifulSoup

from config import IMDB_ID_COLUMN
from pages.imdb_page import ImdbTitlePage

start_time = time.time()


ACTIVE_FIELDS = {
    "Genre": lambda page: page.get_genres(),
    "Languages": lambda page: page.get_languages(),
    "Directors": lambda page: page.get_directors(),
    "Writers": lambda page: page.get_writers(),
    "Cast": lambda page: page.get_cast(top_n=5),
    "Poster": lambda page: page.get_poster_url(),
    "Plot": lambda page: page.get_plot_summary(),
}


# ----------------------------
# Certification extractor
# ----------------------------
def get_certification_from_page(imdb_id, soup):

    try:

        cert = soup.find(
            "a",
            {"href": f"/title/{imdb_id}/parentalguide/?ref_=tt_ov_pg#certificates"}
        )

        if cert:
            return cert.text.strip()

        return "Not Rated"

    except Exception:
        return "Not Rated"


def enrich_dataframe(df: pd.DataFrame, driver) -> pd.DataFrame:

    col_values = {col: [] for col in ACTIVE_FIELDS.keys()}
    certifications = []
    imdb_urls = []
    streaming_logos = []

    total = len(df)

    for idx, imdb_id in enumerate(df[IMDB_ID_COLUMN], start=1):

        imdb_id = str(imdb_id).strip()
        title = df.iloc[idx - 1]["Title"]

        print(f"\nProcessing {idx}/{total}: {title} ({imdb_id})")

        page = ImdbTitlePage(imdb_id, driver)

        imdb_urls.append(page.url)

        # ----------------------------
        # Load IMDb page
        # ----------------------------
        try:
            page.fetch()
        except Exception as e:

            print(f"[ERROR] Page load failed for {imdb_id}: {e}")

            for col_name in ACTIVE_FIELDS.keys():
                col_values[col_name].append("")

            certifications.append("")
            streaming_logos.append("")
            continue


        # ----------------------------
        # Extract fields
        # ----------------------------
        for col_name, getter in ACTIVE_FIELDS.items():

            try:
                value = getter(page)
            except Exception as e:
                print(f"[ERROR] {col_name} failed for {imdb_id}: {e}")
                value = ""

            col_values[col_name].append(value)


        # ----------------------------
        # Certification (same page)
        # ----------------------------
        soup = page.soup

        cert = get_certification_from_page(imdb_id, soup)

        certifications.append(cert)


        # ----------------------------
        # Streaming logos
        # ----------------------------
        try:
            logo_url = page.get_streaming_logo_url()
        except Exception as e:
            print(f"[ERROR] Streaming logo failed for {imdb_id}: {e}")
            logo_url = ""

        streaming_logos.append(logo_url)


        # ----------------------------
        # Progress Monitor
        # ----------------------------
        elapsed = time.time() - start_time
        avg_time = elapsed / idx
        remaining = avg_time * (total - idx)

        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        remaining_str = time.strftime("%H:%M:%S", time.gmtime(remaining))

        print(
            f"\n[{idx}/{total}] {title}\n"
            f"Languages: {col_values['Languages'][-1]}\n"
            f"Directors: {col_values['Directors'][-1]}\n"
            f"Certification: {certifications[-1]}\n"
            f"StreamingLogo: {'Yes' if logo_url else 'No'}\n"
            f"Elapsed: {elapsed_str} | ETA: {remaining_str}"
        )


        # ----------------------------
        # Save checkpoint every 100
        # ----------------------------
        if idx % 100 == 0:

            processed_df = df.iloc[:idx].copy()

            processed_df["IMDB URL"] = imdb_urls

            for col_name, values in col_values.items():
                processed_df[col_name] = values

            processed_df["Certification"] = certifications
            processed_df["StreamingLogo"] = streaming_logos

            checkpoint_file = f"checkpoint_{idx}.csv"

            processed_df.to_csv(checkpoint_file, index=False)

            print(f"Checkpoint saved: {checkpoint_file}")


        # ----------------------------
        # Polite delay
        # ----------------------------
        time.sleep(2)


    # ----------------------------
    # Final dataframe
    # ----------------------------
    df["IMDB URL"] = imdb_urls

    for col_name, values in col_values.items():
        df[col_name] = values

    df["Certification"] = certifications
    df["StreamingLogo"] = streaming_logos

    return df