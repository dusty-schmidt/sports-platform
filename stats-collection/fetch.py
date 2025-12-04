import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from urllib.parse import urlparse

# Load configuration from config.json located in the same directory as this script
config_path = Path(__file__).with_name('config.json')
if not config_path.is_file():
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

def fetch_table(url):
    """Fetch and parse table data from a URL, returning a list of dictionaries."""
    print(f"Fetching URL: {url}")
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Find all tables and look for the data table (usually the first substantial one)
    tables = soup.find_all("table")
    if not tables:
        print(f"No tables found at {url}")
        raise RuntimeError(f"No tables found at {url}")

    # Try to find a table with multiple rows and cells
    data_table = None
    for table in tables:
        rows = table.find_all("tr")
        # Skip tables with less than 2 rows or rows without td/th elements
        if len(rows) < 2:
            continue
        first_row_cells = rows[0].find_all(["th", "td"])
        if len(first_row_cells) < 1:
            continue
        # If first row has text that looks like a description, skip it
        if "Match Charting Project" in first_row_cells[0].get_text():
            continue
        data_table = table
        break
    
    if not data_table:
        # Fallback to first table if none found with criteria
        data_table = tables[0]
        print(f"Using fallback table at {url}")

    rows = data_table.find_all("tr")
    print(f"Found {len(rows)} rows in table at {url}")

    # Find header row (skip descriptive rows)
    header_row = None
    for i, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        # Skip rows with very long text (descriptions)
        if len(cells) > 1 and len(cells[0].get_text()) < 100:
            header_row = row
            break
    
    if not header_row:
        header_row = rows[0]  # Fallback to first row
    
    header_cells = header_row.find_all(["th", "td"])
    headers = [c.get_text(strip=True) for c in header_cells]
    print(f"Headers: {headers}")

    records = []
    for row in rows:
        if row == header_row:
            continue  # Skip header row
        cells = row.find_all("td")
        if not cells:
            continue
        # Ensure number of cells matches headers
        if len(cells) != len(headers):
            continue
        values = [c.get_text(strip=True) for c in cells]
        records.append(dict(zip(headers, values)))

    print(f"Extracted {len(records)} records from {url}")
    return records

def scrape_all():
    """Loop through all URLs in config and save data as JSON files."""
    # Get URLs from config (try different possible key names)
    urls = config.get('tennis data urls', config.get('urls', []))
    
    if not urls:
        print("No URLs found in config file")
        return
    
    # Create data directory
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nFound {len(urls)} URLs to process:")
    for url in urls:
        print(f" - {url}")
    
    # Process each URL
    for url in urls:
        print(f"\nProcessing: {url}")
        try:
            records = fetch_table(url)
            
            # Generate filename from URL
            fname = urlparse(url).path.split("/")[-1].replace(".html", ".json")
            output_path = data_dir / fname
            
            # Save as JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(records)} records to {output_path}")
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

if __name__ == "__main__":
    scrape_all()
