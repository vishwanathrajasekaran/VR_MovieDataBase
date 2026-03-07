# imdb_certification.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time


def get_certification(imdb_id: str, driver) -> str:

    url = f"https://www.imdb.com/title/{imdb_id}/"

    print(f"[DEBUG] Fetching certification for {imdb_id}")

    try:

        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@data-testid='hero__primary-text']")
            )
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        cert = soup.find(
            "a",
            {"href": f"/title/{imdb_id}/parentalguide/?ref_=tt_ov_pg#certificates"}
        )

        if cert:
            certification = cert.text.strip()
            print(f"[DEBUG] Certification for {imdb_id}: {certification}")
            return certification

        return "Not Rated"

    except Exception as e:
        print(f"Error fetching certification for {imdb_id}: {e}")
        return "Not Rated"


def enrich_certifications(input_csv: str, output_csv: str, driver, imdb_column: str = "Const"):

    df = pd.read_csv(input_csv)

    certifications = []

    for i, imdb_id in enumerate(df[imdb_column], start=1):

        imdb_id = str(imdb_id).strip()

        print(f"Processing {i}/{len(df)}: {imdb_id}")

        cert = get_certification(imdb_id, driver)

        certifications.append(cert)

        time.sleep(1)

    df["Certification"] = certifications

    df.to_csv(output_csv, index=False)

    print(f"\n✅ Certification enrichment saved at: {output_csv}")

    return output_csv