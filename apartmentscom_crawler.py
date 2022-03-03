### The University of Chicago
### MACS 30122 Winter 2022
### Final Project
### Group Name: "None"
### Group Members: Chongyu Fang, Feihong Lei, Juno Zhennuo Wu, Coco Jiachen Yu

# Web crawler for scraping apartments.com and extract apartments
# information. We write the data collected to CSV file.

import requests
from bs4 import BeautifulSoup

starting_url = "https://www.apartments.com/chicago-il/1/"

def listing_page_crawler(url):
    """
    This crawler collects the links for every property listed in the
    current listing page.
    
    Input:
        url: the url of the listing page we hope to crawl
        
    Output:
        link_next_page: the link of next page
        lst_apts_link: a list of properties' links
    """

    # Extracting html information of current page
    headers = {"User-Agent":
        "Coco, Juno, Feihong and Chongyu from UChicago"}
    response = requests.get(url, headers = headers, timeout = 300)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Getting the link of next page
    next_page = soup.find("link", rel = "next")
    if next_page == None:
        link_next_page = None
    else:
        link_next_page = soup.find("link", rel = "next").get("href")

    # Extracting all links of properties within current page
    lst_apts_links = []
    apts = soup.find_all("li", class_ = "mortar-wrapper")
    for apt in apts:
        apt_link = apt.find("a").get('href')
        lst_apts_links.append(apt_link)

    return link_next_page, lst_apts_links

def collect_all_apts_links(starting_url):
    """
    Running the listing page crawler and returns
    all property links from the starting url.

    Input:
        starting_url: the url of the page we start

    Output:
        all_apts_links: a list of the links of all the properties
    """

    # Start from the starting page
    page_to_check = starting_url
    next_page_exists = True
    all_apts_links = []

    # Collect links until finished crawling all listing pages
    while next_page_exists:
        page_to_check, apt_links = listing_page_crawler(page_to_check)
        all_apts_links += apt_links
        if page_to_check == None:
            next_page_exists = False

    return all_apts_links

all_properties = collect_all_apts_links(starting_url)

def property_page_crawler(single_property_url):
    """
    Crawler for a single property page. Extract information of
    the features.

    Input:
        single_property_url: the url of a single property

    Output:
        features information
    """

    headers = {"User-Agent":
        "Coco, Juno, Feihong and Chongyu from UChicago"}
    response = requests.get(single_property_url, headers = headers, timeout = 300)
    response_txt = response.text
    soup = BeautifulSoup(response_txt, 'html.parser')
    
    # latitude and longitude
    latitude = soup.find('meta', property = "place:location:latitude")['content']
    longitude = soup.find('meta', property = "place:location:longitude")['content']
    
    # property name
    property_name = soup.find('h1', class_ = 'propertyName').get_text().strip()

    # address
    address_lst = soup.find('div', class_ = 'propertyAddressContainer').find_all('span')[0:3]
    address_lst = [add.get_text() for add in address_lst]
    street = address_lst[0]
    city_state_zip = (address_lst[1] + address_lst[2]).replace('\n', ' ').strip()
    address = street + ', ' + city_state_zip

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

    # security: later computations with crime data

    return latitude, longitude, property_name, address, price_range, bedroom, bathroom, room_area, amenities

# Test code for first five properties
for property_link in all_properties[0:5]:
    p, a, long, lat, pr, be, ba, ra, am = property_page_crawler(property_link)
    print(p, a, long, lat, pr, be, ba, ra, am)