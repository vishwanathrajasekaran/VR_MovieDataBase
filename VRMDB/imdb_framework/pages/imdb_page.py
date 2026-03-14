# pages/imdb_page.py

from typing import Optional
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "https://www.imdb.com/title/"

LOGO_XPATH = (
    '//div[@data-testid="tm-box-woc-text" and '
    '(text()="STREAMING" or text()="PREFERRED" or text()="RENT/BUY")]'
    '/parent::div//img'
)

ROW_ICON_XPATH = '//div[@data-testid="tm-box-update-row"]//img'



class ImdbTitlePage:

    def __init__(self, imdb_id: str, driver):

        self.imdb_id = imdb_id
        self.driver = driver
        self.url = f"{BASE_URL}{imdb_id}/"
        self._soup: Optional[BeautifulSoup] = None


    # -----------------------
    # Load page
    # -----------------------
    def fetch(self):

        print("[DEBUG] Navigating to:", self.url)

        self.driver.get(self.url)

        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@data-testid='hero__primary-text']")
            )
        )

        html = self.driver.page_source

        self._soup = BeautifulSoup(html, "html.parser")


    @property
    def soup(self):

        if self._soup is None:
            self.fetch()

        return self._soup


    # -----------------------
    # Genres
    # -----------------------
    def get_genres(self):

        s = self.soup

        section = s.find("div", {"data-testid": "interests"})

        if not section:
            return ""

        chips = section.find_all("span", class_="ipc-chip__text")

        genres = [chip.get_text(strip=True) for chip in chips]

        return ", ".join(genres)


    # -----------------------
    # Languages
    # -----------------------
    def get_languages(self):

        s = self.soup

        details = s.find("section", {"data-testid": "Details"})

        if not details:
            return ""

        languages = []

        for li in details.find_all("li"):

            label = li.find("span", class_="ipc-metadata-list-item__label")

            if label and "Language" in label.text:

                for a in li.find_all("a"):
                    languages.append(a.text.strip())

        return ", ".join(languages)


    # -----------------------
    # Directors
    # -----------------------
    def get_directors(self):

        s = self.soup

        directors = []

        blocks = s.find_all("li", {"data-testid": "title-pc-principal-credit"})

        for block in blocks:

            label = block.find("span", class_="ipc-metadata-list-item__label")

            if label and "Director" in label.text:

                for a in block.find_all("a"):
                    directors.append(a.text.strip())

        return ", ".join(directors)


    # -----------------------
    # Writers
    # -----------------------
    def get_writers(self):

        s = self.soup

        writers = []

        blocks = s.find_all("li", {"data-testid": "title-pc-principal-credit"})

        for block in blocks:

            label = block.find("span", class_="ipc-metadata-list-item__label")

            if label and "Writer" in label.text:

                for a in block.find_all("a"):
                    writers.append(a.text.strip())

        return ", ".join(writers)


    # -----------------------
    # Cast
    # -----------------------
    def get_cast(self, top_n=5):

        s = self.soup

        section = s.find("section", {"data-testid": "title-cast"})

        if not section:
            return ""

        rows = section.find_all("div", {"data-testid": "title-cast-item"})

        cast = []

        for row in rows[:top_n]:

            actor = row.find("a", {"data-testid": "title-cast-item__actor"})

            if actor:
                cast.append(actor.text.strip())

        return ", ".join(cast)


    # -----------------------
    # Poster
    # -----------------------
    def get_poster_url(self):

        s = self.soup

        poster = s.find("div", {"data-testid": "hero-media__poster"})

        if not poster:
            return ""

        img = poster.find("img")

        if not img:
            return ""

        return img.get("src", "")


    # -----------------------
    # Plot
    # -----------------------
    def get_plot_summary(self):

        s = self.soup

        plot = s.find("span", {"data-testid": "plot-xl"}) or \
               s.find("span", {"data-testid": "plot-l"})

        if not plot:
            return ""

        return plot.text.strip()


    # -----------------------
    # Streaming logos
    # -----------------------
    def get_streaming_logo_url(self):

        try:

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, LOGO_XPATH))
            )

            logos = self.driver.find_elements(By.XPATH, LOGO_XPATH)
            row = self.driver.find_elements(By.XPATH, ROW_ICON_XPATH)

            images = logos + row

            srcs = []

            for img in images:

                src = img.get_attribute("src")

                if src and src not in srcs:
                    srcs.append(src)

            return " | ".join(srcs)

        except:
            return ""

    # -----------------------
    # Episodes (for TV shows)
    # -----------------------
    def get_episode_count(self):

        try:

            time.sleep(2)

            element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@data-testid='hero-subnav-bar-series-episode-count']")
                )
            )

            text = element.text.strip()

            # Example: "1,129 Episodes"
            count = text.split()[0].replace(",", "")

            return count

        except:
            return ""