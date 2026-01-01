# pages/imdb_page.py

from dataclasses import dataclass
from typing import List, Optional
import time
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from imdb_Certification import imdb_certification  

BASE_URL = "https://www.imdb.com/title/"

# Browser-like headers to avoid 403
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.imdb.com/",
    "Connection": "keep-alive",
}

# STREAMING / PREFERRED / RENT/BUY card logo images
LOGO_XPATH = (
    '//div[@data-testid="tm-box-woc-text" and '
    '(text()="STREAMING" or text()="PREFERRED" or text()="RENT/BUY")]'
    '/parent::div//img'
)

# Small row-level icon at the left (for pages like tt9603208)
ROW_ICON_XPATH = '//div[@data-testid="tm-box-update-row"]//img'


@dataclass
class ImdbTitleData:
    imdb_id: str
    url: str
    genres: List[str]
    languages: List[str]
    directors: List[str]
    writers: List[str]
    cast: List[str]
    poster_url: str
    streaming_logos: str  # joined string of logo URLs


class ImdbTitlePage:
    def __init__(self, imdb_id: str):
       self.imdb_id = imdb_id
       self.url = f"{BASE_URL}{imdb_id}/"
       self._soup: Optional[BeautifulSoup] = None

    @property
    def soup(self) -> BeautifulSoup:
        if self._soup is None:
            self.fetch()
        return self._soup


    # -----------------------
    # Basic page fetch (safe + retry)
    # -----------------------
    def fetch(self) -> None:
        import time
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        print(f"[DEBUG] Fetching page HTML: {self.url}")

        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))

        resp = session.get(self.url, headers=HEADERS, timeout=30)
        resp.raise_for_status()

        self._soup = BeautifulSoup(resp.text, "html.parser")

        # polite delay
        time.sleep(2)

    # -----------------------
    # Genres (BeautifulSoup only)
    # -----------------------
    def get_genres(self) -> str:
        s = self.soup
        genres = []

        section = s.find("div", {"data-testid": "interests"})
        if not section:
            print(f"[DEBUG] Genres section not found for {self.imdb_id}")
            return ""

        chips = section.find_all("span", class_="ipc-chip__text")
        for chip in chips:
            text = chip.get_text(strip=True)
            if text:
                genres.append(text)

        joined = ", ".join(genres)
        print(f"[DEBUG] Genres for {self.imdb_id}: {joined}")
        return joined


    # -----------------------
    # Languages
    # -----------------------
    def get_languages(self) -> List[str]:
        s = self.soup
        languages: List[str] = []
        details = s.find("section", {"data-testid": "Details"})
        if not details:
            print(f"[DEBUG] Details section not found for {self.imdb_id}")
            return languages
        lang_rows = details.find_all("li")
        for li in lang_rows:
            label = li.find("span", class_="ipc-metadata-list-item__label")
            if not label:
                continue
            if "Language" in label.get_text(strip=True):
                values = li.find_all("a")
                for a in values:
                    langs = a.get_text(strip=True)
                    if langs:
                        languages.append(langs)
        joined_languages = ", ".join(languages)
        print(f"[DEBUG] Languages for {self.imdb_id}: {joined_languages}")
        return joined_languages

    # -----------------------
    # Directors
    # -----------------------
    def get_directors(self) -> List[str]:
        s = self.soup
        directors: List[str] = []
        credit_blocks = s.find_all("li", {"data-testid": "title-pc-principal-credit"})
        for block in credit_blocks:
            label = block.find("span", class_="ipc-metadata-list-item__label")
            if not label:
                continue
            label_text = label.get_text(strip=True)
            if "Director" in label_text:
                links = block.find_all("a")
                for a in links:
                    name = a.get_text(strip=True)
                    if name:
                        directors.append(name)
        joined_directors = ", ".join(directors)
        print(f"[DEBUG] Directors for {self.imdb_id}: {joined_directors}")
        return joined_directors

    # -----------------------
    # Writers
    # -----------------------
    def get_writers(self) -> List[str]:
        s = self.soup
        writers: List[str] = []
        credit_blocks = s.find_all("li", {"data-testid": "title-pc-principal-credit"})
        for block in credit_blocks:
            label = block.find("span", class_="ipc-metadata-list-item__label")
            if not label:
                continue
            label_text = label.get_text(strip=True)
            if "Writer" in label_text or "Writers" in label_text:
                links = block.find_all("a")
                for a in links:
                    name = a.get_text(strip=True)
                    if name:
                        writers.append(name)
        joined_writers = ", ".join(writers)
        print(f"[DEBUG] Writers for {self.imdb_id}: {joined_writers}")
        return joined_writers

    # -----------------------
    # Cast
    # -----------------------
    def get_cast(self, top_n: int = 5) -> List[str]:
        s = self.soup
        cast_names: List[str] = []
        cast_section = s.find("section", {"data-testid": "title-cast"})
        if not cast_section:
            print(f"[DEBUG] Cast section not found for {self.imdb_id}")
            return cast_names
        rows = cast_section.find_all("div", {"data-testid": "title-cast-item"})
        for row in rows[:top_n]:
            a = row.find("a", {"data-testid": "title-cast-item__actor"})
            if not a:
                continue
            name = a.get_text(strip=True)
            if name:
                cast_names.append(name)
        joined_cast = ", ".join(cast_names)
        print(f"[DEBUG] Cast for {self.imdb_id}: {joined_cast}")
        return joined_cast

    # -----------------------
    # Poster
    # -----------------------
    def get_poster_url(self) -> str:
        s = self.soup
        poster_div = s.find("div", {"data-testid": "hero-media__poster"})
        if not poster_div:
            print(f"[DEBUG] Poster section not found for {self.imdb_id}")
            return ""
        img = poster_div.find("img")
        if not img:
            print(f"[DEBUG] Poster img not found for {self.imdb_id}")
            return ""
        src = img.get("src", "").strip()
    
    # Try to convert to HD by removing resizing params
    # Example: https://m.media-amazon.com/images/M/MV5BZjg1ZjUyYWIt..._QL75_UY281_.jpg
    # Becomes: https://m.media-amazon.com/images/M/MV5BZjg1ZjUyYWIt....jpg
        if "_UX" in src or "_UY" in src or "_QL" in src:
            parts = src.split("_")
            if parts:
                hd_src = "_".join(parts[:-1]) + ".jpg"
                src = hd_src
    
        print(f"[DEBUG] Poster URL (HD) for {self.imdb_id}: {src}")
        return src

    # -----------------------
    # Streaming logos (Selenium headed Chrome)
    # -----------------------
    def get_streaming_logo_url(self) -> str:
        """
        Use Selenium (headed Chrome) to extract logo image URLs
        from STREAMING / PREFERRED / RENT/BUY cards plus the
        small row-level icon where present.
        Returns: 'url1 | url2 | url3' or ''.
        """
        url = self.url
        print(f"[DEBUG] Opening for logo: {url}")

        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)


        try:
            driver.get(url)
            # Wait until at least one card logo appears
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, LOGO_XPATH))
            )

            card_imgs = driver.find_elements(By.XPATH, LOGO_XPATH)
            row_imgs = driver.find_elements(By.XPATH, ROW_ICON_XPATH)

            all_imgs = card_imgs + row_imgs
            if not all_imgs:
                print(f"[DEBUG] No logos found for {self.imdb_id}")
                return ""

            imgs = driver.find_elements(By.XPATH, LOGO_XPATH)
            srcs = []
            for img in all_imgs:
                src = img.get_attribute("src")
                if src and src not in srcs:
                    srcs.append(src)

            joined = " | ".join(srcs)
            print(
                f"[DEBUG] Found {len(srcs)} logo src(s) for {self.imdb_id}: {joined}"
            )
            return joined
        except Exception as e:
            print(f"[DEBUG] Logo NOT found for {self.imdb_id}: {e}")
            return ""
        finally:
            driver.quit()
            time.sleep(5)


    # -----------------------
    # Aggregate helper (optional)
    # -----------------------
    def extract_all(self) -> ImdbTitleData:
        #certificate = get_certification(self.imdb_id)
        genres = self.get_genres()
        languages = self.get_languages()
        directors = self.get_directors()
        writers = self.get_writers()
        cast = self.get_cast(top_n=5)
        poster_url = self.get_poster_url()
        streaming_logos = self.get_streaming_logo_url()

        return ImdbTitleData(
            imdb_id=self.imdb_id,
            url=self.url,
            genres=genres,
            languages=languages,
            directors=directors,
            writers=writers,
            cast=cast,
            poster_url=poster_url,
            streaming_logos=streaming_logos,
        )
