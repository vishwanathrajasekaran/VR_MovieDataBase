# main.py

from data_io import read_input_csv, save_dataframe_csv
from scraper import enrich_dataframe
from imdb_Certification import imdb_certification
from config import OUTPUT_EXCEL_PATH, IMDB_ID_COLUMN

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


if __name__ == "__main__":

    options = webdriver.ChromeOptions()

    options.add_argument(r"--user-data-dir=C:\selenium-profile")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:

        df = read_input_csv()

        enriched_df = enrich_dataframe(df, driver)

        enriched_csv_path = OUTPUT_EXCEL_PATH.replace(".xlsx", "_enriched.csv")

        save_dataframe_csv(enriched_df, enriched_csv_path)

        print(f"Initial enrichment completed: {enriched_csv_path}")

        final_csv_path = OUTPUT_EXCEL_PATH.replace(".xlsx", "_final.csv")

        imdb_certification.enrich_certifications(
            input_csv=enriched_csv_path,
            output_csv=final_csv_path,
            driver=driver,
            imdb_column=IMDB_ID_COLUMN
        )

        print(f"Certification enrichment completed: {final_csv_path}")

    finally:

        driver.quit()