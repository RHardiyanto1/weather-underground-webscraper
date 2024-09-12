import re
import time
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

pd.options.mode.chained_assignment = None

def scrape_weather_data(url):
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # Automatically installs Chrome driver, if unavailible
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)

        # Give the page some time to fully load the dynamic content
        time.sleep(5)

        # Find the table containing daily observations
        table = driver.find_element(By.CLASS_NAME, 'observation-table')
        rows = table.find_elements(By.TAG_NAME, 'tr')
    except Exception as e:
        print(f"Failed to load data from URL: {url}. Error: {e}")
        driver.quit()
        return None

    # Extract table headers
    headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, 'th')]

    # Extract table data
    data = []
    for row in rows[1:]:
        cols = [col.text.strip() for col in row.find_elements(By.TAG_NAME, 'td')]
        data.append(cols)

    # Close the driver
    driver.quit()

    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers)
    return df

def clean_weather_data(df, start_date_str, end_date_str):
    # Convert user input dates to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    current_date = start_date
    date_column = []

    # Trigger to handle blank rows
    blank_row = False

    # Iterate over the rows in the DataFrame
    for index, row in df.iterrows():
        if row.isnull().all():  # Check if the entire row is blank
            blank_row = True
            date_column.append(None)  # Add None for blank rows
        else:
            if blank_row:
                blank_row = False
                current_date += timedelta(days=1)  # Increment the date
            if current_date <= end_date:  # Only add dates up to the end date
                date_column.append(current_date)  # Add the current date
            else:
                date_column.append(None)  # Add None if date exceeds the end date

    # Ensure that date_column matches the length of the DataFrame
    while len(date_column) < len(df):
        date_column.append(None)

    # Add the 'date' column to the DataFrame and drop empty rows
    df['date'] = date_column
    df = df.dropna()

    # Combine 'date' and 'Time' columns into a single datetime column
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['Time'], errors='coerce')

    # Move the 'datetime' column to the leftmost side
    columns = ['datetime'] + [col for col in df.columns if col != 'datetime']
    df = df[columns]

    # Drop redundant Time and date columns
    df = df.drop(columns=['Time', 'date'])

    # Rename columns to include units
    df.rename(columns={
        'Temperature': 'Temperature (F)',
        'Dew Point': 'Dew Point (F)',
        'Humidity': 'Humidity (%)',
        'Wind Speed': 'Wind Speed (mph)',
        'Wind Gust': 'Wind Gust (mph)',
        'Pressure': 'Pressure (in)',
        'Precip.': 'Precipitation (in)'
    }, inplace=True)

    # Convert columns to numeric values, removing non-numeric characters
    for col in ['Temperature (F)', 'Dew Point (F)', 'Humidity (%)', 'Wind Speed (mph)', 'Wind Gust (mph)', 'Pressure (in)', 'Precipitation (in)']:
        df[col] = pd.to_numeric(df[col].str.extract(r'([-+]?[0-9]*\.?[0-9]+)')[0], errors='coerce')

    return df

def get_valid_date(prompt):
    while True:
        date_str = input(prompt)
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please enter the date in yyyy-m-d format.")

def get_valid_url():
    while True:
        url_template = input("Enter the Weather Underground URL (e.g., https://www.wunderground.com/history/daily/country/state/city/code/date/): ").rstrip('/')
        url_template = strip_url_after_date(url_template)
        if validate_url(url_template):
            return url_template
        else:
            print("The URL provided does not match the expected format. Please check and try again.")

def strip_url_after_date(url):
    # Use regex to find the 'date' part and remove everything after it
    match = re.search(r'(https://www\.wunderground\.com/history/daily/.+?/date)', url)
    if match:
        return match.group(1)
    return url

def validate_url(url):
    # Basic check to ensure URL follows the expected pattern
    required_parts = ['history', 'daily', 'date']
    if all(part in url for part in required_parts) and url.startswith('https://www.wunderground.com/'):
        return True
    return False

def main():
    # User input for URL
    url_template = get_valid_url()

    # User input for start and end dates
    start_date = get_valid_date("Enter the start date (yyyy-m-d): ")
    end_date = get_valid_date("Enter the end date (yyyy-m-d): ")

    # Ensure start date is before end date
    if start_date > end_date:
        print("Start date must be before end date. Please re-enter the dates.")
        return

    # Generate list of dates
    date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    # Scrape data for each date
    all_data = []
    for date in date_list:
        date_str = date.strftime('%Y-%m-%d')
        full_url = f"{url_template}/{date_str}"
        print(f"Scraping data for {date_str} from {full_url}...")
        daily_data = scrape_weather_data(full_url)
        if daily_data is not None:
            all_data.append(daily_data)

    # Combine all data into a single DataFrame and clean it
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        cleaned_df = clean_weather_data(final_df, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        # Saving the CSV
        csv_filename = f"scraped_weatherdata.csv"
        cleaned_df.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")
    else:
        print("No data scraped.")

if __name__ == "__main__":
    main()
