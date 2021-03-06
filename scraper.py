import scraper_utils as rmr
import calc_coords as cc
import db_conn as db # to store postings in a MySQL database
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time


def generateSectorURLs(sectorList, lat, lon, zoom):
    sectorPositions = []
    cc.mapSectors(sectorPositions, lat, lon, zoom)
    # Concatenates lat, lon, zoom into URL
    #   lat, lon are to 6 decimal places
    #   Note: using zoom of 14
    for sector in sectorPositions:
        nextSector = "https://www.padmapper.com/?viewType=LIST&lat=" + str(format(sector['latitude'], '.6f')) + "&lng=" + str(format(sector['longitude'], '.6f')) + "&zoom=" + str(14) + "&minRent=100&maxRent=5000&minBR=0&maxBR=10&minBA=1&cats=false&dogs=false"
        sectorList.append(nextSector)
    print("Finished calculating URL's.")

def scrapeSector(sector):
    # Selenium and PhantomJS needed to execute JavaScript and render AJAX-enabled dynamic pages
    driver = webdriver.PhantomJS()
    driver.get(str(sector))
    # Wait until div's of the class 'listing-address' are present before grabbing source
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'listing-address')))
    except TimeoutException:
        driver.save_screenshot('scrapeSectorTimeout.png')
        driver.quit()
        raise TimeoutException()
    driver.save_screenshot('scrapeSectorTimeout.png')
    # Scrolling
    # Load all dynamic content using scrolling DOM actions
    element = driver.find_element_by_class_name("list-container")
    scroll_height = driver.execute_script('return document.getElementsByClassName("list-container")[0].scrollHeight')
    scroll_height_prev = 0
    print("Scraping sector "+sector)
    # Loop to load as many postings as possible
    if element is None:
        print("Element not found")
    finalNumPosts = 0
    while scroll_height != scroll_height_prev:
        pageSource = driver.page_source
        bsObj = BeautifulSoup(pageSource, "html.parser")
        for post in bsObj.findAll("div", {"class": "listing-address"}):
            finalNumPosts += 1
        driver.execute_script('document.getElementsByClassName("list-container")[0].scrollTop = document.getElementsByClassName("list-container")[0].scrollHeight')
        scroll_height_prev = scroll_height
        time.sleep(3) # Scraper courtesy wait
        scroll_height = driver.execute_script('return document.getElementsByClassName("list-container")[0].scrollHeight')
        print(str(scroll_height))

    print("Final number of posts found: " + str(finalNumPosts))
    if finalNumPosts > 0:
        # Final page_source and BS objects after all scrolling complete
        finalSource = driver.page_source
        finalBSObj  = BeautifulSoup(finalSource)

        # List of dictionaries, each describing a post, with the form:
        # [{
        #     "extURL":       extURL,
        #     "listAddr":     listAddr,
        #     "price":        price,
        #     "numBeds":      numBeds,
        #     "latitude":     latitude,
        #     "longitude":    longitude
        # }]
        postings = []

        rmr.getPostsFromPage(driver, finalBSObj, postings)
        # saveToDb(postings)
        driver.quit()

        # Output file, JSON format
        #   Note: 'a' argument allows appending, old file not overwritten
        with open('output.json', 'a') as fout:
            json.dump(postings, fout)

if __name__ == '__main__':
    # Starting point
    lat = 49.251756
    lon = -123.053441
    zoom = 12

    sectorURLs = []
    generateSectorURLs(sectorURLs, lat, lon, zoom)
    for sector in sectorURLs:
        scrapeSector(sector)
