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

        response = urlopen("https://hack-at-uci-backend-maithyy.vercel.app/api/db?query=SELECT%20*%20FROM%20housing")
        json_data = cockroachdb.convertJSONdata(json.loads(response.read()))

        parsed_url = urlparse(webscraper.BASE_URL + self.path)
        print("hello")
        print(parsed_url)
        communities = parse_qs(parsed_url.query)['communities'][0]
        communities = communities.split('_')
        print(communities)
        priceMin = int(parse_qs(parsed_url.query)['priceMin'][0])
        priceMax = int(parse_qs(parsed_url.query)['priceMax'][0])
        bed = int(parse_qs(parsed_url.query)['bed'][0])
        print(bed)
        bath = float(parse_qs(parsed_url.query)['bath'][0])
        print(bath)

        #my_dictionary = {"apartments": cockroachdb.filter([(community_list), (priceMin, priceMax), (bed, bath)])}
        my_dictionary = {"apartments": cockroachdb.filterJSONdata(json_data, communities, priceMin, priceMax, bed, bath)}
        json_object = json.dumps(my_dictionary, indent=4).encode('utf-8')
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(json_object)
        return