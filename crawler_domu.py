"""
The University of Chicago
MACS 30122 Winter 2022
Final Project
Group Name: "None"
Group Members: Chongyu Fang, Feihong Lei, Juno Zhennuo Wu, Coco Jiachen Yu

Web crawler for scraping domu.com and extract the
information of all listed properties/units in Chicago, IL.
We write the data collected to CSV file for further analysis.
"""

import queue
import json
import csv
import re
from bs4 import BeautifulSoup
import requests

#This webcrawler is only designed for Domu website
starting_url = "https://www.domu.com/find/map/markers?sw=36.915759%2C-93.081751&ne=45.852058%2C-85.962611&domu_keys=&domu_search=&places_api=&domu_bedrooms_min=&domu_bedrooms_max=&domu_bathrooms_min=&domu_bathrooms_max=&domu_rentalprice_min=&domu_rentalprice_max=&sort=acttime&page=0"
headers = {"User-Agent": "Coco, Juno, Feihong and Chongyu from UChicago"}

def listing_page_crawler(url,headers):
    """
    This crawler collects the links for every property listed in the
    current listing page.
    Input:
        url: the url of the listing page we hope to crawl
    Output:
        next_page_link: the link of next page
        properties_info_lst: a list of properties' informations 
                    (link,location,price range) in current page
    """
    jscontent = requests.get(url, headers = headers, timeout = 300).text
    jsdict = json.loads(jscontent)
    soup = BeautifulSoup(jsdict["listings"], "html5lib")
    properties_info_lst = []
    next_page_link = None
    
    for line in soup.find_all("div")[0].find_all("div")[3:]:
        a_html = line.find_all("a")

        if a_html!=[]:
            if a_html[-1].text=="next":
                next_page_link = "https://www.domu.com"+a_html[-1].get("href")
                break

        loc = line.get("data-position")
        price = line.get("data-price")
        if a_html!=[] and loc!=None and price!=None:
             properties_info_lst.append(("https://www.domu.com"+a_html[2].get("href"),loc,price))
                
    return next_page_link, properties_info_lst


def get_all_properties_links(starting_url,headers):
    """
    Running the listing page crawler and returns
    all properties links starting from the starting url.
    Input:
        beginning_url: url of the page we begin
    Output:
        all_properties_info: a list of the information (link,location,price range) 
                            of all the properties
    """

    next_page = starting_url
    next_page_exists = True
    all_properties_info = []
    while next_page_exists:
        next_page,current_info = listing_page_crawler(next_page,headers)
        all_properties_info+=current_info
        if next_page==None:
            next_page_exists=False
    
    return all_properties_info


all_properties_links = get_all_properties_links(starting_url,headers)

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

    url = "https://www.domu.com/chicago/north-side/lakeview/one-door-west-apartments/756-w-wellington-ave-3-a-chicago-il-60657"
    headers = {"User-Agent": "Coco, Juno, Feihong and Chongyu from UChicago"}
    response = requests.get(url, headers = headers, timeout = 300)
    soup = BeautifulSoup(response.text, 'html.parser')

    # property name
    property_name = soup.find('h1', class_ = "lb__title").get_text()

    # address
    address = soup.find('h2', class_ = "lb__address").get_text().strip()

    # amenities
    amenities_lst = soup.find('ul', class_ = "glance").find_all('li')
    amenities_lst = [item.get_text() for item in amenities_lst]
    amenities = ', '.join(amenities_lst)

    try:
        # bedroom, bathroom, area range, price_range (for apartments)
        bed_num_lst = []
        bath_num_lst = []
        area_property_range_lst = []
        price_property_range_lst = []

        for tr_tag in soup.find("tbody").find_all("tr"):
            
            bed = tr_tag.find_all("div")[0].text.split("/")[0]
            if bed == "Studio":
                bed_num = 0
            else:
                bed_num = int(bed[0])
            bed_num_lst.append(bed_num)
            

            bath_num = tr_tag.find_all("div")[0].text.split("/")[1][0]
            bath_num_lst.append(bath_num)
            
            area = tr_tag.find_all("div")[1].text
            if "-" in area:
                area = area.split("-")
                area = [a.strip() for a in area]
                area_unit_low = area[0]
                area_unit_high = re.findall(r"[0-9]+", area[1])[0]
                
                area_property_range_lst.append(int(area_unit_low))
                area_property_range_lst.append(int(area_unit_high))
            else:
                area = re.findall(r"[0-9]+", area)[0]
                area_property_range_lst.append(int(area))

            
            price = tr_tag.find_all("div")[2].text
            if "-" in price:
                price = price.split("-")
                price = [p.strip() for p in price]
                price_unit_low = price[0][1:]
                price_unit_high = price[1][1:]

                price_property_range_lst.append(int(price_unit_low))
                price_property_range_lst.append(int(price_unit_high))
            else:
                price = price[1:]
                price_property_range_lst.append(int(price))

            
        bed_min = min(bed_num_lst)
        bed_max = max(bed_num_lst)
        bed = "{} - {} bed".format(bed_min, bed_max)

        ba_min = min(bath_num_lst)
        ba_max = max(bath_num_lst)
        ba = "{} - {} ba".format(ba_min, ba_max)

        area_range_min = min(area_property_range_lst)
        area_range_max = max(area_property_range_lst)
        area_range = "{} - {} sq ft".format(area_range_min, area_range_max)

        price_range_min = min(price_property_range_lst)
        price_range_max = max(price_property_range_lst)
        price_range = "${} - ${}".format(price_range_min, price_range_max)

    except:
        # bedroom, bathroom, area range, price_range (for single units)
        bed = soup.find('div', class_ = "attribute-item bed").get_text()

        ba = soup.find('div', class_ = "attribute-item bath").get_text()

        area_range = soup.find('div', class_ = "lb__basic").get_text()
        area_range = re.findall(r'[0-9]+', area_range)[0]
        area_range = "{} sq ft".format(area_range)

        price_range = soup.find('div', class_ = "lb__price desktop-only").get_text()
        price_range = re.findall(r'\$[0-9,]+', price_range)[0]

    return property_name, address, price_range, bed, ba, area_range, amenities