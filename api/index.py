from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cockroachdb
import webscraper
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        my_dictionary = {"apartments": cockroachdb.filter([(["Vista del Campo", "Camino del Sol"]), (1000, 1200), (2, 2)])}
        json_object = json.dumps(my_dictionary, indent=4).encode('utf-8')
        self.send_header('Content-type','text/plain')
        self.end_headers()
        parsed_url = urlparse(webscraper.BASE_URL + self.path)
        captured_value = parse_qs(parsed_url.query)['communities']
        # self.wfile.write(self.path.encode('utf-8'))
        print(captured_value)
        return
