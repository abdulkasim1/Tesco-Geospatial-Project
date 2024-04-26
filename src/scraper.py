import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from selenium import webdriver


def get_page_source(url):
    driver = webdriver.Chrome("chromedriver_mac64/chromedriver")
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.close()
    return soup

#def get_area_details
def get_stores(url):
    soup = get_page_source(url)
    stores = soup.find_all("a", class_="Directory-listLink")

    store_area = np.array([])
    store_count = np.array([])
    store_links = np.array([])

    for link in stores:
        area = link.text
        
        link_url = ("https://www.tesco.com/store-locator/" + link.get("href"))
        count = re.sub(r'[^0-9]', '', link.get("data-count"))
        store_area = np.append(store_area, area)
        store_count = np.append(store_count, count)
        store_links = np.append(store_links, link_url)

    data = np.stack((store_area, store_count, store_links), axis=1)
    return data
    

def get_all_stores(url):
    data = get_stores(url)

    #Empty array for all store links
    all_store_links = []

    #Append stores where store_count==1 since these are direct links to each store
    store_count_1 = data[data[:, 1] == "1"]
    all_store_links = store_count_1[::, 2]
    
    #For areas where store_count!=1 need to get array of links for each area which will be used to scrape data for each store
    store_count_more_than_1 = data[data[:, 1] != '1']
    store_links_more_than_1 = store_count_more_than_1[:, 2]

    for link in store_links_more_than_1:
        url = link
        driver = webdriver.Chrome("chromedriver_mac64/chromedriver")
        driver.get(url)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        store_links = soup.find_all('a', class_='Button Teaser-button')
    
        for link in store_links:
            link_url = ("https://www.tesco.com/store-locator/" + link.get('href'))
            all_store_links = np.append(all_store_links, link_url)

    return all_store_links

def get_store_details(url):
    all_store_links = get_all_stores(url)

    store_titles = []
    store_types = []
    store_postcodes = []
    store_geo_positions = []

    for link in all_store_links:
        url = link
        driver = webdriver.Chrome("chromedriver_mac64/chromedriver")
        driver.get(url)
        
        soups = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()

        soup_store_title = soups.find('span', class_='Core-title Heading--lead')
        store_title = soup_store_title.text

        store_title_split = store_title.split()
        store_type = store_title_split[-1]

        soup_postocde = soups.find('span', class_='Address-field Address-postalCode')
        store_postcode = soup_postocde.text

        soup_geo_postion = soups.find('meta', attrs={"name": "geo.position"})
        geo_postion = soup_geo_postion.get("content").replace(";", ", ")

        
        store_titles = np.append(store_titles, store_title)
        store_types = np.append(store_types, store_type)
        store_postcodes = np.append(store_postcodes, store_postcode)
        store_geo_positions = np.append(store_geo_positions, geo_postion)  

    store_details = np.stack((store_titles, store_types, store_postcodes, store_geo_positions), axis=1)
    df = pd.DataFrame(store_details, columns=["Name", "Type", "Postcode", "Geo_position"])
    df.to_csv("tesco_stores.csv", index=False)
    return df

if __name__ == "__main__":
    get_store_details("https://www.tesco.com/store-locator/directory")