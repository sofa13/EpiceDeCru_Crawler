import urllib.request
from urllib.parse import urlsplit, urlunsplit, quote
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import csv
import sys

def iri2uri(iri):
    """
    Convert an IRI to a URI (Python 3).
    """
    uri = ''
    if isinstance(iri, str):
        (scheme, netloc, path, query, fragment) = urlsplit(iri)
        scheme = quote(scheme)
        netloc = netloc.encode('idna').decode('utf-8')
        path = quote(path)
        query = quote(query)
        fragment = quote(fragment)
        uri = urlunsplit((scheme, netloc, path, query, fragment))

    return uri

def main():

	rootURL = "https://spicetrekkers.com"
	boutiqueExtension = '/boutique'
	
	storeItemURLs = []
	storeItemData = []
	
	CatagoryPageURLS = []

	rootPageReq = urllib.request.Request(iri2uri(rootURL + boutiqueExtension), headers={'User-Agent' : "Magic Browser"}) 
	rootPage = BeautifulSoup(urllib.request.urlopen(rootPageReq), 'lxml', parse_only=SoupStrainer(class_='Boutique__listing'))


	listings = rootPage.find('div', class_='Boutique__listing')

	for article in listings.find_all('article'):
		
		
		boutiqueCatagoryURL = rootURL + article.a['href']
		catagoryPageReq = urllib.request.Request(iri2uri(boutiqueCatagoryURL), headers={'User-Agent' : "Magic Browser"}) 
		catagoryPage = BeautifulSoup(urllib.request.urlopen(catagoryPageReq), 'lxml', parse_only=SoupStrainer(['a','div']))
		
		#print(boutiqueCatagoryURL)
		
		allCatagoryPages = [{'URL': boutiqueCatagoryURL, 'Page': catagoryPage}]
		CatagoryPageURLS.append(boutiqueCatagoryURL)
		
		nextPageURL = ''
		currentCatagoryPage = catagoryPage
		while currentCatagoryPage is not None:
			nextPage = currentCatagoryPage.find('a', class_='Pagination__page Pagination__page--next')
			currentCatagoryPage = None
			if nextPage is not None and nextPage['href'] not in CatagoryPageURLS:
				nextPageReq = urllib.request.Request(nextPage['href'], headers={'User-Agent' : "Magic Browser"}) 
				currentCatagoryPage = BeautifulSoup(urllib.request.urlopen(nextPageReq), 'lxml', parse_only=SoupStrainer(['a','div']))
				allCatagoryPages.append({'URL': nextPage['href'], 'Page': currentCatagoryPage})
				CatagoryPageURLS.append(nextPage['href'])
				#print(nextPage['href'])
		
		
		for catagoryPage in allCatagoryPages:
		
			print(catagoryPage['URL'])
		
			storeItems = catagoryPage['Page'].find('div', class_='StoreItem__grid')

			for storeItem in storeItems.find_all('div', class_='StoreItem'):
				
				storeItemURL = storeItem.find('div', class_='StoreItem__container').a['href']
				storeItemStatus = True if storeItem.find('div', class_='StoreItem__btn-addCart') is not None else False

				if storeItemStatus and storeItemURL not in storeItemURLs:
				
					storeItemURLs.append(storeItemURL)
				
					req = urllib.request.Request(iri2uri(storeItemURL), headers={'User-Agent' : "Magic Browser"}) 
					
					storeItemPage = BeautifulSoup(urllib.request.urlopen(req).read(), 'lxml', parse_only=SoupStrainer('div'))
					
					storeItemVariants = storeItemPage.find_all('div', class_='ProductDetails_variant')
					
					storeItemTitle = ''
					storeItemDescription = ''
					hasWeight = False
					variantPriceAndWeights = []
					
					for storeItemVariant in storeItemVariants:
					
						storeItemVariantShortDesc = storeItemVariant.find('div', class_='ProductDetails__short-desc').get_text()
						
						weightIndex = storeItemVariantShortDesc.find('Weight :')		
						
						if weightIndex != -1:
							
							if not hasWeight:
								storeItemTitle = storeItemPage.find('div', class_='ProductDetails__global').h1.string.strip()
								storeItemDescriptionTag = storeItem.find('div', class_='StoreItem__description')
								for p in storeItemDescriptionTag.descendants:	#this tag can have any number of underlying <p> tags, get the furthest 'depth' one for description
									storeItemDescription = p.string
								if storeItemDescription == '':
									storeItemDescription = storeItemDescriptionTag.string
							
							storeItemVariantPriceTag = storeItemVariant.find('div', class_='ProductDetails__price')
							if storeItemVariantPriceTag is None:
								storeItemVariantPriceTag = storeItemVariant.find('div', class_='ProductDetails__price -with-promo')	#When on discount
							storeItemVariantPrice = storeItemVariantPriceTag.get_text().strip()
							
							
							storeItemVariantWeight = storeItemVariantShortDesc[weightIndex + 8:].strip()
							storeItemVariantPriceFloat = float(storeItemVariantPrice[0:storeItemVariantPrice.index('$')].strip())
							storeItemVariantWeightInGrams = float(storeItemVariantWeight[0:storeItemVariantWeight.index('g')].strip())
							dollarPerGramRatio = storeItemVariantPriceFloat / storeItemVariantWeightInGrams
						
							variantPriceAndWeights.append({
							'Price': storeItemVariantPriceFloat, 
							'Weight': storeItemVariantWeightInGrams, 
							'PriceRatio': dollarPerGramRatio,
							})
						
							hasWeight = True
				
					if hasWeight:
						sortedVariantPriceAndWeights = sorted(variantPriceAndWeights, key=lambda k: k['PriceRatio']) 
						storeItemData.append({
						'Title': storeItemTitle, 
						'PriceAndWeights': sortedVariantPriceAndWeights,
						'Description': storeItemDescription.strip() if storeItemDescription is not None else '',
						'URL': storeItemURL
						})
						print(storeItemURL + ' [ADDED]')
				
				elif not storeItemStatus:
					print(storeItemURL + '[OUT OF STOCK]')
				else:
					print(storeItemURL + ' [ALREADY CHECKED]')
			





		
	sortedStoreItemDataByPriceRatio = sorted(storeItemData, key=lambda k: k['PriceAndWeights'][0]['PriceRatio']) 
			
	keys = sortedStoreItemDataByPriceRatio[0].keys()
	with open('StoreItems.csv', 'w') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(sortedStoreItemDataByPriceRatio)

if __name__ == "__main__":
    main()