import scrapy
import pycountry
from locations.items import GeojsonPointItem
from locations.categories import Code
from typing import List,Dict
from bs4 import BeautifulSoup
import uuid
import re

class FincomunSpider(scrapy.Spider):
    name = 'fincomun_dac'
    brand_name = 'Fincomun'
    spider_type: str = 'chain'
    spider_chain_id = "21967"
    spider_categories: List[str] = [Code.BANK]
    spider_countries: List[str] = [pycountry.countries.lookup('mx').alpha_3]
    allowed_domains: List[str] = ['fincomun.com.mx']
    start_urls = ['https://www.fincomun.com.mx/sucursales/']


    def start_requests(self):
        '''
        Spider entrypoint.
        Request chaining starts here.
        '''
        url: str = "https://www.fincomun.com.mx/sucursales/"

        yield scrapy.Request(
            url,
            callback=self.parse
        )


    def parse(self,response):
        '''
        @url https://www.fincomun.com.mx/sucursales/
        @returns items 80 100
        @scrapes ref chain_id chain_name addr_full website lat lon
        '''
        
        soup=BeautifulSoup(response.text,'lxml')
        address_cont = soup.find_all("div",id="divsuc1")
        latlong_cont= soup.find_all("div",id="divsuc2")
        

        for i in range(len(address_cont)):
            address = address_cont[i].find('span',class_="text_suc").text
            address = address.replace("D.", "")
            address_parts=address.split("T.")
            map_url=latlong_cont[i].find("a")["href"] 
            longitude_match = re.search(r'!2d(-?\d+\.\d+)!', map_url)
            latitude_match = re.search(r'!3d(-?\d+\.\d+)!', map_url)
            latitude = float(latitude_match.group(1))
            longitude = float(longitude_match.group(1))
            
            data = {
                'ref': uuid.uuid4().hex,
                'chain_id': '21967',
                'chain_name': 'Fincomun',
                'addr_full': address_parts[0].strip(),
                'website': 'https://www.fincomun.com.mx/',
                'lat': latitude,
                'lon': longitude

            }

            yield GeojsonPointItem(**data)