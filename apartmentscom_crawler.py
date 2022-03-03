"""
The University of Chicago
MACS 30122 Winter 2022
Final Project
Group Name: "None"
Group Members: Chongyu Fang, Feihong Lei, Juno Zhennuo Wu, Coco Jiachen Yu

Web crawler for scraping apartments.com and extract the
information of all listed properties in Chicago, IL.
We write the data collected to CSV file for further analysis.
"""

import requests
from bs4 import BeautifulSoup
import csv

def listing_page_crawler(url):
    """
    This crawler collects the links for every property listed in the
    current listing page.

    Input:
        url: the url of the listing page we hope to crawl

    Output:
        next_page_link: the link of next page
        properties_links_lst: a list of properties' links in current page
    """

    headers = {"User-Agent":
        "Coco, Juno, Feihong and Chongyu from UChicago"}
    response = requests.get(url, headers = headers, timeout = 300)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Getting the link of next page
    next_page = soup.find("link", rel = "next")
    if next_page == None:
        next_page_link = None
    else:
        next_page_link = soup.find("link", rel = "next").get("href")

    # Extracting all links of properties within current page
    properties_links_lst = []
    properties = soup.find_all("li", class_ = "mortar-wrapper")
    for property in properties:
        property_link = property.find("a").get('href')
        properties_links_lst.append(property_link)

    return next_page_link, properties_links_lst

def get_all_properties_links(beginning_url):
    """
    Running the listing page crawler and returns
    all properties links starting from the starting url.

    Input:
        beginning_url: url of the page we begin

    Output:
        all_properties_links: a list of the links of all the properties
    """

    # Start from the beginning url
    next_page = beginning_url
    next_page_exists = True
    all_properties_links = []

    # Collect links until finished crawling all listing pages
    while next_page_exists:
        next_page, current_links = listing_page_crawler(next_page)
        all_properties_links += current_links
        # Condition to exit loop
        if next_page == None:
            next_page_exists = False

    return all_properties_links

def property_page_crawler(url):
    """
    Crawler for a single property page. Extract information of
    the features.

    Input:
        url: the url of a single property page

    Output:
        property_name (str): name of property
        address (str): address of property
        latitude (float): latitude of property
        longitude (float): longitude of property
        price_range (str): the price range of apts in the property
        bedroom (str): bedroom # range of apts in the property
        bathroom (str): bathroom # range of apts in the property
        room_area (str): area range of apts in the property
        amenities (str): amenities and features
    """

    headers = {"User-Agent":
        "Coco, Juno, Feihong and Chongyu from UChicago"}
    response = requests.get(url, headers = headers, timeout = 300)
    soup = BeautifulSoup(response.text, 'html.parser')

    # property name
    property_name = soup.find('h1', class_ = 'propertyName').get_text().strip()

    # address
    address_lst = soup.find('div', class_ = 'propertyAddressContainer').find_all('span')[0:3]
    address_lst = [add.get_text() for add in address_lst]
    street = address_lst[0]
    city_state_zip = (address_lst[1] + address_lst[2]).replace('\n', ' ').strip()
    address = street + ', ' + city_state_zip

    # latitude and longitude
    latitude = float(soup.find('meta', property = "place:location:latitude")['content'])
    longitude = float(soup.find('meta', property = "place:location:longitude")['content'])

    # price range, bedroom, bathroom, room area
    rent_info_lst = soup.find_all('p', class_ = 'rentInfoDetail')

    price_range = rent_info_lst[0].get_text()
    bedroom = rent_info_lst[1].get_text()
    bathroom = rent_info_lst[2].get_text()
    room_area = rent_info_lst[3].get_text()

    # amenities
    amenities_lst = soup.find_all('p', class_ = 'amenityLabel')
    amenities_lst = [amenity.get_text() for amenity in amenities_lst]
    amenities = ', '.join(amenities_lst)

    return property_name, address, latitude, longitude, price_range, bedroom, bathroom, room_area, amenities

def go(output_filename, all_properties_links):
    """
    Writer for the csv file.

    Input:
        output_filename: the name of the output csv file
        all_properties_links: links of all single property's pages
    """

    with open (output_filename, 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        header = ['property_name',
                    'address',
                    'latitude',
                    'longitude',
                    'price_range',
                    'bedroom',
                    'bathroom',
                    'room_area',
                    'amenities']
        writer.writerow(header)

        # Write data
        for property_link in all_properties_links:
            p, a, lat, long, pr, be, ba, ra, am = property_page_crawler(property_link)
            row = [p, a, lat, long, pr, be, ba, ra, am]
            writer.writerow(row)


if __name__ == "__main__":
    beginning_url = "https://www.apartments.com/chicago-il/1/"
    all_properties_links = get_all_properties_links(beginning_url)
    output_filename = 'apartments.csv'

    go(output_filename, all_properties_links)
