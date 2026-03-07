# main.py

from data_io import read_input_csv, save_dataframe_csv
from scraper import enrich_dataframe
from config import OUTPUT_EXCEL_PATH

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

        print(f"\n✅ Enrichment completed: {enriched_csv_path}")

    finally:

        driver.quit()