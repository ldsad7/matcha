import requests
import json
import urllib.parse
from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/api/v1/datalistLocations', methods=['GET', 'POST'])
def callAvito():
   return requests.get("https://www.avito.ru/web/1/slocations?locationId=637640&limit=10&q=" + request.args.get('value')).text

@app.route('/')
def home():
   return render_template('main.html')


if __name__ == '__main__':
   app.run(debug=True)