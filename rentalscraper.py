from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
import pymysql
import time
import re
import logging

# PyMySQL connects scraper to MySQL database
connection = pymysql.connect(host='localhost',
                       user='root',
                       password='PASSWORD', # use your local db's pw
                       db='mysql')

cursor = connection.cursor()
db = "your_db_name"  # replace with whatever your databases' name is
cursor.execute("USE "+db)

# Generate SQL queries
# Use whatever parameters you want to find. I am using the link to the actual posting, generic address, price, and number of available bedrooms as mine
def storePrelim(extURL, listAddr, price, numBeds):
    regexp = "your_regexp"     # Insert whatever regexp defines your desired site
    standard = re.compile(regexp)
    if not (standard.match(extURL)): extURL = NULL
    tableName = "your_table_name" # replace with table name
    cursor.execute("INSERT INTO "+tableName+" (extURL, listAddr, price, numBeds) VALUES (\"%s\", %s, %s)", (extURL, listAddr, price, numBeds))
    cursor.connection.commit()

    #TODO: only add new postings if link is not present in the table
    # cursor.execute("ALTER IGNORE TABLE listings ADD UNIQUE extURL", extURL)
    # cursor.connection.commit()

# Store latitude and longitude data based on the stored data's lid
def storeLatLon(lat, lon, lid):
    cursor.execute("UPDATE "+tableName+" SET latitude=%(lat)s, longitude=%(lon)s WHERE listingID = %(lid)s", {'lat':lat, 'lon':lon, 'lid':lid})
    cursor.connection.commit()

# Get URL's from your database (if you choose to store them in storePrelim())
def getURLs():
    cursor.execute("SELECT listingID, extURL FROM "+tableName+" WHERE extURL IS NOT NULL")
    links = cursor.fetchall()
    return links

# Selenium and PhantomJS needed to execute JavaScript and render AJAX-enabled dynamic pages
pjs = webdriver.PhantomJS()
pjs.get("https://www.webpage.com") # Insert your favorite webpage to begin crawling
pageSource = pjs.page_source

# Scrolling function
# TODO: use PhantomJS' scrollTop property to load all dynamic content


# Create a BS object from driver's page source
bsObj = BeautifulSoup(pageSource)

# Get immediate child of listing-preview that contains URL to actual posting
#   Tag: a href="URL"
def getExtURL(post):
    extURL = post.find("a")
    extURL = extURL['href']
    return extURL

# TODO: Get listing pic
#   Tag: div class="listing-image" data-original="PIC URL"
# def getListImg(post):
#     listImg = post.find("div", {"class":"listing-image"})
#     listImg = listImg['data-original']
#     #print("URL found:", listImg)
#     return listImg

# Get listing address
#   Tag: div class="listing-address"
#   Ex. 123 Name St, City, XX, NNN NNN
def getListAddr(post):
    listAddr = post.find("div", {"class":"listing-address"}).get_text()
    return listAddr

# Get price per month
#   Tag: immediate div child of div class="listing-properties"
#   Ex. $706
def getPrice(post):
    price = post.find("div", {"class":"listing-properties"}).find("div").get_text()
    price = int(re.sub('[\$\,]', '', price))
    return price

# Get number of beds
#   Tag: div class="listing-num-bedrooms"
#   Ex. 1 Bed (Can be studio)
def getNumBeds(post):
    numBeds = post.find("div", {"class":"listing-num-bedrooms"}).get_text()
    studio = re.compile("[Studio]*?")
    if (studio.match(numBeds)): # studios are 1 br
        numBeds = 1
    else:
        numBeds = int(re.sub('[Beds]', '', numBeds.strip()))
    return numBeds

# Get a posting preview div on page
#   Tag: div class="listing-preview"
posts = 0
for post in bsObj.findAll("div", {"class":"listing-preview"}):
    if (post.get_text() == ''): break # scraper has hit the last div so end
    try:
        storePrelim(getExtURL(post), getListAddr(post), getPrice(post), getNumBeds(post))
        posts += 1
    except: # log all exceptions to debug after trial runs
        logging.basicConfig(filename="store_prelim.log", level=logging.DEBUG)
        logging.exception('storePrelim()', exc_info=True)
        pass

print("Finished storing " + str(posts) + " listings.")

# Now to step into each link for latitudes and longitudes
# DB will be updated on each link entry
numLinks = 0
listToCrawl = getURLs()
print("Finding latitudes and longitudes for " + str(len(listToCrawl)) + " listings.")
for pair in listToCrawl: # pair is a tuple of (lid, extURL)
    regexp_2 = "your_other_regexp"
    pageType = re.compile(regexp_2)
    # Load pair into PhantomJS
    lid  = pair[0]
    link = str(pair[1])
    try:
        html = urlopen(link)
        bsObj = BeautifulSoup(html)
        # If the pair leads to a specific page
        # Note: add more clauses if looking for multiple page types
        if (pageType.match(link)):
            latLonTag = "some_tag"
        # Otherwise the pair is of another page type
        else:
            latLonTag = "some_other_tag"
        # Find latitude and longitude for a post
        # Each can usually be found in page metadata (super easy yay), otherwise change to suit tags of your desired page
        lat = bsObj.find("meta", {"property":latLonTag+":location:latitude"})['content']
        lon = bsObj.find("meta", {"property":latLonTag+":location:longitude"})['content']
        try:
            storeLatLon(lat, lon, lid)
            numLinks += 1
        except: # log all exceptions to debug after trial runs
            logging.basicConfig(filename="store_latlon.log", level=logging.DEBUG)
            logging.exception('storeLatLon()', exc_info=True)
            pass
    except URLError:
        pass

print("Finished finding latitudes and longitudes for " + str(numLinks) + " listings.")
pjs.close()
cursor.close()
connection.close()
