# Plate class in order to store the data for each plate
class plateInfo:
    def __init__(self, company, link, weight, price, stock):
        self._company = company
        self._link = link
        self._weight = weight
        self._price = price
        self._stock = stock
        self._display = (weight, price, stock)

    def getInfo(self):
        return list(self._display)

    def getStock(self):
        return self._stock

    def getPrice(self):
        return self._price

    def getWeight(self):
        return self._weight

    def getCompany(self):
        return self._company

#Imports
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup
import lxml

#For Twitter
#Page: https://twitter.com/CastPrice
import tweepy as tp
import os
APIKey = "Lhcnye2K3sKUiwimLwz0ET2qt"
APISecretKey = "5EVmjTS2Q59K2gnTg2kGHwpDbKRHwIMFDDXwYB4lnSjnXuQAfv"
AccessToken = "1334966865731448832-8k0oBUnUotF5oCKDMj8THsAOKoR4xh"
AccessTokenSecret = "3pGY3nSHhqVn9znwnaXojfKASTORiBWAitSPVWa155ZIh"
BearerToken = "AAAAAAAAAAAAAAAAAAAAAOtsKQEAAAAAyowOIGR2YX47m4XaTx0AeMy2s1g%3DzWKIDDcTXLCQlFEXrl4Rwe8gndWqyPMeGDeSMujqZ61s7iWf0G"
#Login
auth = tp.OAuthHandler(APIKey, APISecretKey)
auth.set_access_token(AccessToken, AccessTokenSecret)
api = tp.API(auth)

# Driver Setup (Only used for Rogue and York)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/usr/local/bin/chromedriver", options=options)

#Function to find min price for a given weight. If all out of stock, will return the min
#price among all the out of stock plates
def minPrice(weight, plateList):
    inStockPrice = []
    inStockCompany = []
    outStockPrice = []
    outStockCompany = []
    for plate in plateList:
        if(plate.getWeight() == weight):

            if(plate.getStock() == "Out of Stock"):
                outStockPrice.append(plate.getPrice())
                outStockCompany.append(plate.getCompany())
            else:
                inStockPrice.append(plate.getPrice())
                inStockCompany.append(plate.getCompany())

    if(len(inStockPrice) == 0):
        minVal = min(outStockPrice)
        minComp = outStockCompany[outStockPrice.index(minVal)]
        return "No in stock " + str(weight) + "s. Lowest out of stock is " + str(minComp) + " at $" + str(minVal)
    else:
        minVal = min(inStockPrice)
        minComp = inStockCompany[inStockPrice.index(minVal)]
        return "Cheapest in stock of " + str(weight) + " is " + str(minComp) + " at $" + str(minVal)

#List of all plates
allPlates = []

#Scrape for Titan Fitness
url = "https://www.titan.fitness/strength/weight-plates/cast-iron-plates/cast-iron-olympic-plates/CPLATE_GROUP.html"
r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')

company = "Titan Fitness"
plates = soup.findAll("div", class_="set-item")

header = ("Weight", "Price", "Stock")
print(list(header))

# Looping through all Plate listings
for plate in plates:
    # Link
    link = plate.select_one(".product-name a")["href"]
    link = "titan.fitness" + link

    # Price
    price = plate.find("span", class_="sup-hide").text.strip()
    price = float(price[1:])

    # Weight
    weightString = plate.find("h3", class_="product-name").text.strip()
    weight = []
    for t in weightString.split():
        try:
            weight.append(float(t))
        except ValueError:
            pass
    weight = weight[0]

    # Stock
    stock = plate.find("span", class_="availability-msg").text.strip()
    if "out" in stock:
        stock = "In Stock"
    else:
        stock = "Out of Stock"

    #Make plate object and add to list of all plates
    resultPlate = plateInfo(company, link, weight, price, stock)
    allPlates.append(resultPlate)

# Scrape for York Barbell (using selenium)
url = "https://yorkbarbell.com/product/2-inch-cast-iron-olympic-plate/"
company = "York Barbell"
link = url

#Finding all the plates
driver.get(url)
plates = driver.find_elements_by_class_name("attached")

#Iterates through dropdown menu of weights
for x in range(len(plates)):

    # Weight (Before click)
    weightString = plates[x].text.strip()
    weight = []
    for t in weightString.split():
        try:
            weight.append(float(t))
        except ValueError:
            pass
    weight = weight[0]

    # Clicks each dropdown option
    plates[x].click()
    time.sleep(1)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    # Price
    priceString = soup.select_one(".woocommerce-variation-price").text.strip()
    length = len(priceString)
    price = float(priceString[1:length])

    # Stock
    stock = soup.select_one(".woocommerce-variation-availability").text.strip()
    if(stock == "Out of stock"):
        stock = "Out of Stock"

    #Refreshes plate list, makes plate object, and adds to list of plates
    plates = driver.find_elements_by_class_name("attached")
    resultPlate = plateInfo(company, link, weight, price, stock)
    allPlates.append(resultPlate)

# Scrape for Rogue Fitness (using selenium)
url = "https://www.roguefitness.com/rogue-olympic-plates?gclid=Cj0KCQiAlZH_BRCgARIsAAZHSBlVDa0HIv_X2ChS5SpidgShkRbWHE4rAtYiChwfHKxorzGCDMQAu7gaAjlXEALw_wcB"
company = "Rogue Fitness"
link = url

# Iterating through the dropdown and automating clicking
driver.get(url)

#Finding lists for each necessary element of the plate
weights = driver.find_elements_by_class_name("item-name")
prices = driver.find_elements_by_class_name("item-price")
stocks = driver.find_elements_by_class_name("add-to-cart")

#Iterates through the plates
for x in range(len(weights)):

    # Weight
    weightString = weights[x].text.strip()
    weight = []
    for t in weightString.split("LB"):
        try:
            weight.append(float(t))
        except ValueError:
            pass
    weight = weight[0]

    # Price
    price = prices[x].text.strip()
    price = float(price[1:len(price)])/2

    # Stock
    if (stocks[x].text.strip() == "Notify Me"):
        stock = "Out of Stock"
    else:
        stock = "In Stock"

    #Makes plate object and adds to list of plates
    resultPlate = plateInfo(company, link, weight, price, stock)
    allPlates.append(resultPlate)

driver.close()

for x in allPlates:
    print(x.getInfo())

#Finding min price for each weight, makes it into a string
minTwoFive = minPrice(2.5, allPlates)
minFive = minPrice(5, allPlates)
minTen = minPrice(10, allPlates)
minTwentyFive = minPrice(25, allPlates)
minThirtyFive = minPrice(35, allPlates)
minFourtyFive = minPrice(45, allPlates)

print(minTwoFive)
print(minFive)
print(minTen)
print(minTwentyFive)
print(minThirtyFive)
print(minFourtyFive)

api.update_status(minTwoFive + " " + minFive + " " + minTen)
api.update_status(minTwentyFive + " " + minThirtyFive + " " + minFourtyFive)
