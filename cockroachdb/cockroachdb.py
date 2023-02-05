import os
import psycopg2
from pony.orm import Database, PrimaryKey, Required, db_session, between
import json
import re
import webscraper

# Web scrape ONCE + insert into db
def initialize():
    api_links = [webscraper.getAPIURL(community) for community in webscraper.COMMUNITIES]
    json_data = [webscraper.getJSONdata(link) for link in api_links ]

    for _ in json_data:
        community = json["Title"]
        for route in json["TermsFilter"]["Values"]:
            term = route["Text"].split(":")[0] # Ex: Fall 2023
            if str(webscraper.CURRENT_YEAR) not in term:
                break
            api_url = webscraper.BASE_URL + route["Route"]
            myJSON = webscraper.getJSONdata(api_url)
            for property in myJSON["Attributes"]:
                title = property["Title"]
                if "Bed" not in title:
                    bed, bath = 1, 1 #assuming it is studio/efficiency
                else:
                    bed, bath = re.findall(r'\d+\.\d+|\d+', property["Title"])
                    bed, bath = int(bed), float(bath)
                if property["SqFt"] != "": #some dont have sizes
                    size = int(re.findall(r'\d+', property["SqFt"])[0])
                else:
                    size = 0
                price = int(re.findall(r'\d+', property["Price"])[0])
                image = webscraper.BASE_URL + property["ImageURL"]
                floor_id = property["FloorplanID"]

                insert(floor_id, community, term, title, price, bed, bath, size, image)

# Create a cursor.
# pg_conn_string = os.environ["PG_CONN_STRING"]
pg_conn_string = "postgresql://audrey:4_eNA6opk5yE0-S9vaCY5g@zothome-database-4915.6wr.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"
connection = psycopg2.connect(pg_conn_string)

# Set to automatically commit each statement
connection.set_session(autocommit=True)

cursor = connection.cursor()

# create table
def create_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS housing (id INT community CHAR NOT NULL, term CHAR, title CHAR, price INT NOT NULL, num_beds INT NOT NULL, num_baths DECIMAL NOT NULL, size INT NOT NULL, image CHAR")

# insert data into db
def insert(floor_id, comm, term, img, title, price, num_beds, num_baths, size):
    cursor.execute(f"INSERT INTO housing VALUES ({floor_id}, {comm}, {term}, {title}, {price}, {num_beds}, {num_baths}, {size}, {img})")

# query database for filters
db = Database()

class Home(db.Entity):
    _table_ = 'housing'
    id = PrimaryKey(int)
    community = Required(str)
    term = Required(str)
    title = Required(str)
    price = Required(int)
    num_beds = Required(int)
    num_baths = Required(float)
    size = Required(int)
    image = Required(str)

# bind db object to cockroachdb
db.bind('postgres', pg_conn_string)

# create table if it doesn't exist
db.generate_mapping(create_tables=True)
initialize()

# filters_list structure: [(k,v), (k, v)...] with first being community key
@db_session
def filter(filters_list):
    # [(tuple of community names), (price min, price max), (beds, baths)]
    # if empty, add all
    communities = filters_list[0]
    communities_list = []
    
    if communities.length() == 0:
        subset = Home.select(h for h in Home)
        
    for c in communities:
        subset = Home.select(lambda home : Home.community == c)

    # filter by price: (price min, price max)
    min = filters_list[1][0]
    max = filters_list[1][1]
    subset = subset.select(h for h in Home if between(h.price, min, max))

    for row in subset:
        print(row.to_dict())

    # filter by beds/baths: (beds, baths)
    beds = filters_list[2][0]
    baths = filters_list[2][1]
    if beds != "any":
        subset = subset.select(h for h in Home if h.num_beds >= beds)
    if baths != "any":
        subset = subset.select(h for h in Home if h.num_baths >= baths)

    for s in subset:
        communities_list.append(s.to_dict)
        print(s.to_dict)
    
    #list of dictionaries describing rows
    return communities_list