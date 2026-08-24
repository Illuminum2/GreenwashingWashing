# GreenwashingWashing

Crawls a website and reports every page containing a greenwashing related word.

## Install
```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```
`playwright install` is needed for `SCRAPING_MODE = "dynamic"`.

## Run
Set the patterns in [config.toml](config.toml), then pass the target site:
```bash
python ./src/main.py <url>
```
Matches are printed to the console, or written to `output.csv` with `PRINT_MODE = "csv"`.
