# Weather Underground Webscraper

A simple webscraper made for a another project. It collects the hourly weather information from the site wunderground.com.

## Features
- Scrapes daily weather data from Weather Underground, with the location and date range of your choice
- Cleans and formats the scraped data automatically, and saves as a CSV file for easy analysis.
- Script uses 'webdriver_manager' to automatically install ChromeDriver, without you needing to manually download it. (Just make sure your chrome browser is up to date)

## Requirements

- Python >= 3.7
- Selenium
- Pandas
- WebDriver Manager

## Sample run:

```bash
python weather_scraper.py
Enter the Weather Underground URL (e.g., https://www.wunderground.com/history/daily/country/state/city/code/date/): https://www.wunderground.com/history/daily/us/ny/new-york-city/KLGA/date/
Enter the start date (yyyy-m-d): 2023-06-01
Enter the end date (yyyy-m-d): 2023-06-30
Scraping data for 2023-06-01 from https://www.wunderground.com/history/daily/us/ny/new-york-city/KLGA/date/2023-06-01...
...
Scraping data for 2023-06-01 from https://www.wunderground.com/history/daily/us/ny/new-york-city/KLGA/date/2023-06-30...
Data saved to scraped_weatherdata.csv
```

## Getting the correct URL

Go to https://www.wunderground.com/history and find the location you want and get the link. 

Sometimes the link will be in different format than shown on the example, as long as it follows the general guideline of `https://www.wunderground.com/history/daily/ ... /date/` it should work.

Though if wunderground change how their site is formatted, it might render the script unsuable and needs to be updated, but as of September 2024, it works just fine.

## Known Issue

Console might spam you with SSL handshake errors, each time it tries to scrape the website, but it will collect the data just fine. I am out of ideas on how to suppress/fix this, but for the purposes of the script, it will collect the data regardless.
