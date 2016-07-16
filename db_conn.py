import pymysql
import re

# PyMySQL connects scraper to MySQL database
connection = pymysql.connect(host='localhost',
                       user='root',
                       password='PASSWORD', # replace with your db's password
                       db='mysql')

cursor = connection.cursor()
db = "your_db_name"  # replace with your databases' name
cursor.execute("USE "+db)

# Generate SQL queries
# Use whatever parameters you want to find. I am using: url to the actual posting, generic address, price, and number of available bedrooms as mine
def storeGeneral(extURL, listAddr, price, numBeds):
    # Insert whatever regexp defines your desired site
    regexp = "your_regexp"
    standard = re.compile(regexp)
    if not (standard.match(extURL)): extURL = NULL
    tableName = "your_table_name" # replace with table name
    cursor.execute("INSERT INTO "+tableName+" (extURL, listAddr, price, numBeds) VALUES (\"%s\", %s, %s)", (extURL, listAddr, price, numBeds))
    cursor.connection.commit()

# Store latitude and longitude data based on the stored data's lid
def storeLatLon(lat, lon, lid):
    cursor.execute("UPDATE "+tableName+" SET latitude=%(lat)s, longitude=%(lon)s WHERE listingID = %(lid)s", {'lat':lat, 'lon':lon, 'lid':lid})
    cursor.connection.commit()

# Get URL's from your database (if you choose to store them in storeGeneral())
def getURLs():
    cursor.execute("SELECT listingID, extURL FROM "+tableName+" WHERE extURL IS NOT NULL")
    links = cursor.fetchall()
    return links
