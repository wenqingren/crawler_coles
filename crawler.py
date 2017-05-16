import json
import os
from selenium import webdriver
import re

CHROME_ENV = "webdriver.chrome.driver"
DIRNKS_MAIN_PAGE = "https://shop.coles.com.au/a/a-national/everything/browse/drinks?pageNumber=1"
SUB_CAT_DRINKS_PAGE = "https://shop.coles.com.au/a/a-national/everything/browse/drinks/{}pageNumber={}"
PRODUCT_URL = "https://shop.coles.com.au/a/a-national/product/{}"


def crawl(fp):
    def product_iter(sub_cats):
        # loop into the sub categories of drinks
        for sub_url in sub_cats:
            page_num = 1
            while True:
                driver.get(SUB_CAT_DRINKS_PAGE.format(sub_url, page_num))
                print "Checking page: {}".format(SUB_CAT_DRINKS_PAGE.format(sub_url, page_num))
                urlpat = re.compile(r' href="/a/a-national/product/(.*?)"')
                # get the products list in the page
                products = urlpat.findall(driver.page_source)
                if products:
                    for product in set(products):
                        driver.get(PRODUCT_URL.format(product))
                        try:
                            urlpat = re.compile(r'<strong class="product-price">(.*?)</strong>')
                            price = urlpat.findall(driver.page_source)[0]
                            urlpat = re.compile(r'<span class="product-name" aria-hidden="true" data-ng-bind="::productDisplayVM.product.displayNameText">(.*?)</span>')
                            name = urlpat.findall(driver.page_source)[0]
                            urlpat = re.compile(r'<p data-ng-bind-html="::productDisplayVM.product.longDescription.sanitizeHtml\(\)">(.*?)</p>')
                            description = urlpat.findall(driver.page_source)[0]
                        except IndexError:
                            pass
                        else:
                            product_dict = {"url": PRODUCT_URL.format(product), "name": name,
                                            "description": description, "price": price}
                            yield product_dict
                    page_num += 1
                else:
                    break

    chromedriver = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver")
    os.environ[CHROME_ENV] = chromedriver
    driver = webdriver.Chrome(chromedriver)

    driver.get(DIRNKS_MAIN_PAGE)
    urlpat = re.compile(r' href="/a/a-national/everything/browse/drinks/(.*?)?pageNumber=1')
    sub_categories = urlpat.findall(driver.page_source)
    
    for product in product_iter(set(sub_categories)):
        fp.write(json.dumps(product) + "\n")
            

if __name__ == "__main__":  
    with open('json_results.txt', 'w') as fp:
        crawl(fp)
