# main.py
from data_io import read_input_csv, save_dataframe_csv
from scraper import enrich_dataframe
from imdb_Certification import imdb_certification  # import the module
from config import OUTPUT_EXCEL_PATH, IMDB_ID_COLUMN

if __name__ == "__main__":
    # 1️. Load input CSV
    df = read_input_csv()

    # 2️. Enrich IMDb data (genres, languages, directors, cast, poster, streaming)
    enriched_df = enrich_dataframe(df)
    enriched_csv_path = OUTPUT_EXCEL_PATH.replace(".xlsx", "_enriched.csv")  # use CSV
    save_dataframe_csv(enriched_df, enriched_csv_path)
    print(f"Initial enrichment completed: {enriched_csv_path}")

    # 3️. Add Certification column
    final_csv_path = OUTPUT_EXCEL_PATH.replace(".xlsx", "_final.csv")
    imdb_certification.enrich_certifications(
        input_csv=enriched_csv_path,
        output_csv=final_csv_path,
        imdb_column=IMDB_ID_COLUMN
    )
    print(f"Certification enrichment completed: {final_csv_path}")
