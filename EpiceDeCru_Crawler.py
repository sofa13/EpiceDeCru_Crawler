# Sort epice de cru items from least expensive to most expensive, by weight
# e.g. something that costs $10 for 10g is less then something that costs $5 for 1g.
# Things to keep in mind... 
# ... check if weight of item is given, if not skip item 
# ... check if item is in stock, if not skip item 
# ... be sure to handle duplicate items, since some items are in several elements

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import sys
from pprint import pprint

import time

username = ""
password = ""

class EpiceDeCru_Crawler:

	def __init__(self):
		self.driver = webdriver.Chrome()
		self.wait = WebDriverWait(self.driver, 60)

	def vt_more(self, url):
		print(url)

		driver = self.driver
		wait = self.wait

		driver.get(url)

		# waiting for presence of an element
		time.sleep(2)
		
		# get elements
		elements = driver.find_elements_by_xpath("//div[@class='Boutique__listing']/article/a")
		
		elementLinks = [link.get_attribute("href") for link in elements]
		pprint(elementLinks)
		
		for link in elementLinks:
			print(link)
			
			driver.get(link)
			
			# waiting for presence of an item
			time.sleep(2)
			
			# get items
			items = driver.find_elements_by_xpath('//div[@class="StoreItem__container"]/a')
			
			itemLinks = [link.get_attribute("href") for link in items]
			pprint(itemLinks)

if __name__ == '__main__':

	ct = EpiceDeCru_Crawler()

	ct.vt_more("https://epicesdecru.com/boutique")
