# Tesco Geospatial Project

## Web scraping
The aim was to scrape and collect data on store information for all Tesco supermarkets in the UK. This included information about the type of store it is (extra, express, superstore), postcode and latitude, and longitude points. Python was used throughout the project and specifically for this step BeautifulSoup, Selenium, and Webdriver were used.

## Generating polygons
Thereafter, using this information to generate polygons to imitate catchment areas. So each Tesco Express and superstore was matched to its nearest Tesco Extra by calculating distances between stores. This led to each Tesco Extra having several stores matched to it forming a polygon. Geopandas, scipy, shapely, and folium packages were used for this step

## Visualising data
The next step was to visualize this data. This was done by plotting all the stores and polygons by creating an interactive map. This was done using the folium package.

## Why is this work useful?

So this piece of work was a proof of concept and was further developed. All UK supermarket stores were introduced and geographic locations similar to postcodes were used as the central point of the polygons instead of Tesco Extra stores. Other amenities were also used such as swimming pools, sports halls, and artificial grass pitches.

This analysis allows to make conclusions such as identifying areas that have good access to relatively cheaper foods (as supermarkets tend to sell cheaper food compared to corner shops) and those areas with not-so-good access. Similar conclusions can be made for other amenities.