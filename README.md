# Greenwashing Washing

Crawls a website and reports every page containing greenwashing related words.
Pages are fetched asynchronously and every word is matched against the RegEx patterns in [config.toml](src/gww/config.toml).
The matches are written to the console or a CSV file.

This is in response to the [EU Directive 2024/825](https://eur-lex.europa.eu/eli/dir/2024/825/oj/eng), which bans generic unproven environmental claims like "climate neutral" or "eco-friendly".

## Features

- **Async crawling**: Recursive crawling with a configurable maximum depth
- **Two scraping modes**: `static` uses raw aiohttp requests, `dynamic` uses a Playwright chromium instance
- **Sitemap support**: The crawl starts from the site root and the sitemap
- **Pattern matching**: Case-insensitive match and exclusion patterns, preconfigured for English, German and Dutch
- **Caching**: Responses are cached on disk with a configurable expiry
- **Retries**: Failed requests are retried with an exponential backoff and jitter
- **Output**: Print the matches to the console or write them to a CSV file

## Install

```bash
python3.14 -m venv .venv
source .venv/bin/activate
uv sync
playwright install chromium
```

`playwright install chromium` is only needed for the `dynamic` scraping mode.

## Run

Set the match patterns in [config.toml](src/gww/config.toml), then pass the target site:

```bash
gww <url>
```

The URL must include the scheme (https/http) and the full host:

```bash
gww https://books.toscrape.com/
```

## Options

- **`url`**: Base website URL, must include scheme (https/http) and full host
- **`-s`, `--static`**: Use aiohttp requests (raw network requests) for scraping
- **`-d`, `--dynamic`**: Use playwright (chromium instance) for scraping
- **`-c`, `--cache-skip`**: Skip the cache and always make a new network request


- **`-r`, `--reset`**: Overwrite the global configuration file with the default and exit
- **`-h`, `--help`**: Show the help message and exit

Without `-s` or `-d` the scraping mode falls back to [`crawl.default_mode`](src/gww/config.toml) in [config.toml](src/gww/config.toml), if that is not defined, `static` is used. 
The output target is set with [`print.mode`](src/gww/config.toml), which takes `console` or `csv`.

## Configuration

To override the global configuration, create a [config.toml](src/gww/config.toml) clone to the working directory and edit it:

`cp src/gww/config.toml .`

## License

This project is licensed under the [MIT License](LICENSE.md).
