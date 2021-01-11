# Tagesschau Subtitle Word Occurrences

This repo enables the scraping, cleaning and analyzing of the subtitles of the tagesschau, the German daily news show.

![Example Plot](imgs/plot_example.png)

The scraper `scraper/` scrapes show subtitles and show metadata from [tagesschau.de](tagesschau.de).

## Installation
``` bash
pip3 install -r requirements.txt
```

## Usage
`python3 scraper/main.py` scrapes the data from all available tagesschau shows from today 

## Inspiration

At the 36C3, the Chaos Communication Congress of the Chaos Computer Club e.V., the talk [Vom Ich zum Wir - Gesellschaftlicher Wandel in den Reden im Bundestag](https://media.ccc.de/v/36c3-10993-vom_ich_zum_wir) was held by maha and Kai Biermann. 

Tl;dw: They created [this tool](https://www.zeit.de/politik/deutschland/2019-09/bundestag-jubilaeum-70-jahre-parlament-reden-woerter-sprache-wandel), which makes a word occurrence analysis over time with the protocols of the German Bundestag.
