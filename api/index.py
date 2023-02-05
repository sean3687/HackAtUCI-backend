from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cockroachdb
import json
import webscraper
from urllib.request import urlopen

class handler(BaseHTTPRequestHandler):

    # handle get requests - parse url, filter db, return json
    def do_GET(self):
        self.send_response(200)

        response = urlopen("https://hack-at-uci-backend-maithyy.vercel.app/api/db?query=SELECT%20*FROM%20housing")
        print(response.read())

        parsed_url = urlparse(webscraper.BASE_URL + self.path)
        communities = parse_qs(parsed_url.query)['communities']
        community_list = communities.split('_')
        priceMin = parse_qs(parsed_url.query)['priceMin']
        priceMax = parse_qs(parsed_url.query)['priceMax']
        bed = parse_qs(parsed_url.query)['bed']
        bath = parse_qs(parsed_url.query)['bath']

        my_dictionary = {"apartments": cockroachdb.filter([(community_list), (priceMin, priceMax), (bed, bath)])}
        json_object = json.dumps(my_dictionary, indent=4).encode('utf-8')
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(json_object)
        return