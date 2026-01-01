# pages/imdb_certification.py
import pandas as pd
import requests
from lxml import html
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

def get_certification(imdb_id: str) -> str:
    url = f"https://www.imdb.com/title/{imdb_id}/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        xpath = f'//a[@href="/title/{imdb_id}/parentalguide/?ref_=tt_ov_pg#certificates"]'
        elements = tree.xpath(xpath)
        if elements:
            cert = elements[0].text_content().strip()
            return cert if cert else "Not Rated"
        return "Not Rated"
    except Exception as e:
        print(f"Error fetching certification for {imdb_id}: {e}")
        return "Not Rated"

def enrich_certifications(input_csv: str, output_csv: str, imdb_column: str = "Const") -> str:
    df = pd.read_csv(input_csv)
    if imdb_column not in df.columns:
        raise ValueError(f"Column '{imdb_column}' not found in CSV")
    
    certifications = []
    for i, imdb_id in enumerate(df[imdb_column], start=1):
        print(f"Processing {i}/{len(df)}: {imdb_id}")
        cert = get_certification(str(imdb_id))
        certifications.append(cert)
        print(f"✅ {imdb_id} | Certification: {cert}")
        time.sleep(1)
    
    df['Certification'] = certifications
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Certification enrichment saved at: {output_csv}")
    return output_csv
