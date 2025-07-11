# Amazon Product Listing Scraper

This project provides a Python-based web scraper designed to extract publicly available product information from Amazon.com listings. The scraper is built with reliability and flexibility in mind, allowing users to collect valuable data for various purposes such as price comparison, market research, or competitor analysis.

## Description

The Amazon Product Listing Scraper navigates Amazon product pages and extracts key details, including product titles, prices, descriptions, ratings. The project leverages popular Python libraries for web scraping to efficiently parse HTML content and structure the extracted data.
* **Structured Data Output**:
  The extracted data is organized into a clean and easy-to-use format (e.g., CSV, JSON), facilitating further analysis and integration with other applications.
* **Potential applications include**:
    * **Price Monitoring**: Track the prices of specific products over time to identify trends or competitive pricing strategies.
    * **Market Research**: Gather data on product features, customer reviews, and ratings to understand market trends and consumer preferences.
    * **Competitive Analysis**: Monitor competitor product listings and pricing to inform business decisions.
**Disclaimer**
Please note that scraping Amazon.com may be subject to their Terms of Service. While this tool is designed to scrape publicly available information, users should be mindful of Amazon's policies and ensure responsible and ethical scraping practices. Using proxies and implementing rate limits can help in minimizing the risk of IP blocking or other issues. Always review the terms of service of any website before scraping.
AI responses may include mistakes. Learn more

## Getting Started

### Dependencies
  This project requires:
  * Python 3.8+
  
  * Google Chrome (latest)
  
  * ChromeDriver (auto-managed via script)
  
  * The following Python packages:
    * selenium>=4.10.0
    * requests
    * wget
    * openpyxl  # for Excel (.xlsx) file support
    * pandas    # only if reading from Excel

### Installing

1. Clone the repository
  ```
  git clone https://github.com/yourusername/amazon-listing-scraper.git
  cd amazon-listing-scraper
  ```
2. Set up a Python virtual environment (optional but recommended)
  ```
  python -m venv venv
  source venv/bin/activate        # Mac/Linux
  venv\Scripts\activate           # Windows
  ```
3. Install Python dependencies
  ```
  pip install -r requirements.txt
  ```
4. Download the ChromeDriver (cross-platform)
  The script will auto-detect your OS and download the correct version of ChromeDriver:
  ```
  python -c "from amazon_listings import download_latest_driver; download_latest_driver()"
  ```
### Program Execution

* Run with ASINs directly from the command line:
  ```
  python amazon_listings.py -a B09G3HRMVP -a B0C7SVP66F
  ```
* Or provide a file of ASINs:
  ```
  python amazon_listings.py -f asin_list.csv
  ```
* Accepted input formats:

  * .txt – One ASIN per line
  * .csv – Single-column file
  * .xlsx – Excel file with ASINs
  * .json – Key-value pairs or list

* Optional Chrome Options:
  You can pass Chrome flags (e.g. headless mode) via --options:
  ```
  python amazon_listings.py -a B09G3HRMVP --options "--headless=new"## Help
  ```
