import os
import psycopg2
from pony.orm import Database, PrimaryKey, Required, db_session, between, select
import re
import webscraper
from dotenv import load_dotenv

# load environment variables
load_dotenv()

def create_table():
    cursor.execute("DROP TABLE IF EXISTS housing")
    cursor.execute("CREATE TABLE IF NOT EXISTS housing (id STRING PRIMARY KEY, community STRING NOT NULL, term STRING, title STRING, price INT NOT NULL, num_beds INT NOT NULL, num_baths DECIMAL NOT NULL, size INT NOT NULL, image STRING)")

# insert data into db
def insert(floor_id, comm, term, title, price, num_beds, num_baths, size, img):
    cursor.execute("INSERT INTO housing VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (floor_id, comm, term, title, price, num_beds, num_baths, size, img))

# filters_list structure: [(k,v), (k, v)...] with first being community key
@db_session
def filter(filters_list):
    # [(tuple of community names), (price min, price max), (beds, baths)]
    # if empty, add all
    communities = filters_list[0]
    communities_list = []
    print("is filter runnning")

    if len(communities) == 0:
        subset = Home.select(h for h in Home)
    else: 
        subset = Home.select(lambda home : home.community in communities)
    

    # filter by price: (price min, price max)
    min = filters_list[1][0]
    max = filters_list[1][1]
    subset = select(h for h in subset if between(h.price, min, max))

    # filter by beds/baths: (beds, baths)
    beds = filters_list[2][0]
    baths = filters_list[2][1]
    if beds != "any": # remind front end to pass "any" as string if they dont select any beds or baths
        subset = select(h for h in subset if h.num_beds >= beds)
    if baths != "any":
        subset = select(h for h in subset if h.num_baths >= baths)

    for s in subset:
        print(s.to_dict())

    #list of dictionaries describing rows
    return communities_list

# Web scrape ONCE + insert into db
def initialize():
    id = 0
    create_table()
    api_links = [webscraper.getAPIURL(community) for community in webscraper.COMMUNITIES]
    json_data = [webscraper.getJSONdata(link) for link in api_links ]

    for theJSON in json_data:
        community = theJSON["Title"]
        for route in theJSON["TermsFilter"]["Values"]:
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
                if "-" in property["Price"]:
                    price = property["Price"].split("-")[0]
                price = int(re.findall(r'\d+', property["Price"])[0])
                image = webscraper.BASE_URL + property["ImageURL"]
                #floor_id = property["FloorplanID"]

                insert(id, community, term, title, price, bed, bath, size, image)
                id += 1



# Create a cursor.
pg_conn_string = os.getenv("PG_CONN_STRING")
connection = psycopg2.connect(pg_conn_string)

# Set to automatically commit each statement
connection.set_session(autocommit=True)

cursor = connection.cursor()

initialize()

# query database for filters
db = Database()

# pony orm - query
class Home(db.Entity):
    _table_ = 'housing'
    id = PrimaryKey(str)
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

filter([(["Vista del Campo", "Camino del Sol"]), (1000, 1200), (2, 2)])