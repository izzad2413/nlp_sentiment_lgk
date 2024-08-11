from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
from typing import List
import os

@dataclass
class Business:
    """holds business data
    """
    name: str = None
    address: str = None
    reviews_count: int = None
    reviews_average: float = None
    category: str = None
    # coordinate: str = None

@dataclass
class BusinessList:
    """holds list of Business objects, 
       and save to both excel and csv
    """
    business_list: List[Business] = field(default_factory=list)
    
    def dataframe(self):
        """transform business_list to pandas dataframe 

        Returns: pandas dataframe
        """
        return pd.json_normalize((asdict(business) for business in self.business_list), sep="_")
    
    def save_to_csv(self, filename):
        """saves pandas dataframe to csv file

        Args:
            filename (str): filename 
        """
        directory = 'C:/Users/asus/Documents/personal_project/nlp_sentiment_lgk/data/raw'
        os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist
        filepath = os.path.join(directory, f'{filename}.csv')
        self.dataframe().to_csv(filepath, index=False)  # Save the CSV file using the full path


def main():
    
    with sync_playwright() as p:
        
        print('===Connecting===')
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.google.com/maps', timeout=60000)
        # wait is added for dev phase. can remove it in production
        print('===Connection Successful===')
        
        page.locator('//input[@id="searchboxinput"]').fill(search_for) # search engine
        page.keyboard.press('Enter')
        
        # path
        list_path = '//div[@class="Nv2PK THOPZb CpccDe "]'
        
        # scrolling 
        page.hover('(//div[@class="Nv2PK THOPZb CpccDe "])[1]')

        # this variable is used to detect if the bot
        # scraped the same number of listings in the previous iteration
        previously_counted = 0
        while True:
            page.mouse.wheel(0, 200000)
            
            if page.locator(list_path).count() >= total:
                listings = page.locator(list_path).all()[:total]
                print(f'Total Scraped: {len(listings)}')
                break
            else:
                # logic to break from loop to not run infinitely 
                # in case arrived at all available listings
                if page.locator(list_path).count() == previously_counted:
                    listings = page.locator(list_path).all()
                    print(f'Arrived at all available\nTotal Scraped: {len(listings)}')
                    break
                else:
                    previously_counted = page.locator(list_path).count()
                    print(f'Currently Scraped: ', page.locator(list_path).count())
        
        business_list = BusinessList()
        
        # scraping
        for listing in listings:
        
            listing.click()
            # page.wait_for_selector('meta[itemprop=image]', state='visible', timeout=5000)
            page.wait_for_timeout(5000)
            name_xpath = '//h1[@class="DUwDvf lfPIob"]'
            address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
            reviews_span_xpath = '(//span[@class="ceNzKf"])[1]'
            category_xpath = '//button[@class="DkEaL "]'
            # coordinate_xpath = '(//div[@class="mLuXec"])[1]'
            # coordinate_element = page.locator('meta[itemprop=image]').first() 
        
            business = Business()
            
            # extracting the feature, if exist scrape else return null
            if page.locator(name_xpath).count() > 0:
                business.name = page.locator(name_xpath).inner_text()
            else:
                business.name = ''
            if page.locator(address_xpath).count() > 0:
                business.address = page.locator(address_xpath).inner_text()
            else:
                business.address = ''
            if listing.locator(reviews_span_xpath).count() > 0:
                aria_label = listing.locator(reviews_span_xpath).get_attribute('aria-label')
                if aria_label:
                    split_label = aria_label.split()

                    if len(split_label) > 0:
                        business.reviews_average = float(split_label[0].replace(',', '.').strip())
                    else:
                        business.reviews_average = ''

                    # Check if there are enough elements for the reviews count
                    if len(split_label) > 2:
                        reviews_count_str = split_label[2].strip().replace(',', '')
                        business.reviews_count = int(reviews_count_str) if reviews_count_str.isdigit() else 0
                    else:
                        business.reviews_count = 0
                else:
                    business.reviews_average = ''
                    business.reviews_count = 0
              
            #     business.reviews_average = float(aria_label.split()[0].replace(',', '.').strip())
            #     reviews_count_str = aria_label.split()[2].strip().replace(',', '')
            #     business.reviews_count = int(reviews_count_str) if reviews_count_str.isdigit() else 0
            # else:
            #     business.reviews_average = ''
            #     business.reviews_count = 0
            if page.locator(category_xpath).count() > 0:
                business.category = page.locator(category_xpath).inner_text()
            else:
                business.category = ''
            # if coordinate_xpath.count() > 0:
            #     business.coordinate = coordinate_element.get_attribute("content")
            # else:
            #     business.coordinate = ''
            
            # combine the dataset extracted    
            business_list.business_list.append(business)

        filename = search_for.replace(" ", "_")  # Generate the filename based on the search query
        # saving to a csv just to showcase the features.
        business_list.save_to_csv(filename)
        
        print('===Scraping Complete===')
        browser.close()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()
    
    if args.search:
        search_for = args.search
    else:
        # in case no arguments passed
        # the scraper will search by default for:
        search_for = 'langkawi cenang restaurant'
    
    # total number of products to scrape. Default is 120
    if args.total:
        total = args.total
    else:
        total = 120
        
    main()
    
# to run it type, python googlemap.py --search "your search query" --total 100