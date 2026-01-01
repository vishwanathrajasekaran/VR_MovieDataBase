# VRMDB – IMDb Web Scraper
VRMDB is a Python-based web scraper that extracts movie data from IMDb and stores it in CSV files for further analysis and exploration.

# Features
•	Scrapes movie details from IMDb pages using Python.
•	Enriches data with genres, languages, directors, writers, cast, poster images, and streaming platform information.
•	Saves raw and enhanced data into CSV files.
•	Configurable via a central config module.
•	Modular architecture with separate files for scraping, page parsing, and data I/O.
•	Supports certification lookup for movies and TV titles.

# Project Structure
## File / Folder	Purpose
1. main.py	Entry point; orchestrates the complete scraping and enrichment workflow. Loads input CSV, enriches with IMDb data, and adds certification information.
2. scraper.py	High-level scraper logic; iterates over IMDb IDs and coordinates page parsing and data extraction.
3. imdb_page.py	IMDb page parser; uses BeautifulSoup and Selenium to extract movie attributes (genres, cast, directors, streaming logos, poster URLs) from HTML content.
4. data_io.py	Helpers to read input CSVs and write enriched output CSVs.
5. config.py	Central configuration file containing base URLs, file paths, column names, and HTTP headers.
6. imdb_certification.py	Module for fetching and adding certification data (G, PG, PG-13, R, etc.) to the output.
7. 31-12-2025.csv	Base input dataset with initial IMDb IDs and title information.
8. Enhanced_31-12-2025.csv	Final enriched dataset with all extracted IMDb metadata.
9. VRMDB.pyproj	Visual Studio Python project file.

# Prerequisites
•	Python: 3.9 or higher (64-bit) installed on Windows.
•	Virtual Environment: Recommended for isolated dependency management.

# Required Libraries
1. Install dependencies using pip:
2. pip install requests beautifulsoup4 selenium lxml pandas

# Key libraries:
• requests – HTTP library for fetching IMDb pages
•	beautifulsoup4 – HTML parsing
•	selenium – Automated browser for JavaScript-heavy content (streaming logos)
•	lxml – Fast XML/HTML parsing backend
•	pandas – Data manipulation and CSV I/O

# Configuration
## Update config.py to control:
•	IMDB_BASE_URL – Base URL for IMDb title pages (default: https://www.imdb.com/title/)
•	INPUT_EXCEL_PATH – Path to input CSV file containing IMDb IDs
•	OUTPUT_EXCEL_PATH – Path where enriched CSV will be saved
•	IMDB_ID_COLUMN – Column name in input CSV containing IMDb IDs (default: "Const")
•	HEADERS – Browser-like HTTP headers to avoid 403 errors

# Example Configuration
1. IMDB_BASE_URL = "https://www.imdb.com/title/"
2. INPUT_EXCEL_PATH = r"D:\Users\ADMIN\source\repos\VRMDB\VRMDB\imdb_framework\Data\31-12-2025.csv"
3. OUTPUT_EXCEL_PATH = r"D:\Users\ADMIN\source\repos\VRMDB\VRMDB\imdb_framework\Data\Enhanced_31-12-2025.csv"
4. IMDB_ID_COLUMN = "Const"

# How to Run
1. From the project root directory:
2. python main.py

# Execution Flow
1. Load Input CSV – main.py reads the base CSV with IMDb IDs from the path specified in config.py.
2. Enrich with IMDb Data – scraper.py iterates over each IMDb ID, calling imdb_page.py to extract:
o	Genres
o	Languages
o	Directors and writers
o	Top 5 cast members
o	Poster image URL
o	Streaming platform logos (using Selenium)
3.	Save Enriched Data – Results saved to *_enriched.csv with all extracted metadata.
4.	Add Certifications – imdb_certification module fetches certification data (e.g., PG-13, R) and adds it to the final CSV.
5.	Output Final CSV – Complete enriched dataset saved to *_final.csv.

The entire process includes polite delays (2–5 second gaps) between requests to respect IMDb's server load and terms of service.

# Output Files
The script generates multiple CSV files:
*_enriched.csv	Base dataset + genres, languages, directors, writers, cast, posters, streaming info
*_final.csv	Enhanced data + certification ratings (G, PG, PG-13, R, etc.)

Each row corresponds to one IMDb title with all extracted metadata in separate columns.

# Platform
This project was scripted and executed on:
•	Operating System: Windows 10/11
•	IDE: Microsoft Visual Studio 2022 with Python workload enabled, using a .pyproj-based Python project file
•	Python Runtime: Python 3.9+ (64-bit) configured as the default interpreter within Visual Studio
•	Development Environment: Multi-monitor setup with simultaneous web scraping and data inspection tasks
The scripts can also run from the Windows command line or any other IDE as long as a compatible Python 3.9+ environment is available.

# Future Enhancements
•	Add comprehensive logging for monitoring long scraping runs
•	Implement exponential backoff and circuit breaker pattern for network resilience
•	Parameterize date-based filenames instead of hardcoding (e.g., {date}_enriched.csv)
•	Add unit tests and integration tests for imdb_page.py selectors
•	Support for batch processing and multi-threading to accelerate large datasets
•	Database storage option (SQLite, PostgreSQL) as alternative to CSV

# Troubleshooting
403 Forbidden errors:
•	The script includes browser-like headers and retry logic. If still blocked, add delays between requests in config.py or use a proxy.
Selenium Chrome driver not found:
•	Ensure ChromeDriver is installed and in the system PATH, or specify its path explicitly in imdb_page.py.
Timeout errors:
•	Increase the timeout value in ImdbTitlePage.fetch() or adjust polite delay intervals in scraper.py.
Missing data in output:
•	Check that IMDb page selectors in imdb_page.py (XPath, CSS classes) are still valid; IMDb updates its HTML structure periodically.

# References
•	IMDb Official Website: https://www.imdb.com
•	BeautifulSoup Documentation: https://www.crummy.com/software/BeautifulSoup/
•	Selenium Documentation: https://selenium.dev/documentation/
•	Requests Documentation: https://requests.readthedocs.io/

