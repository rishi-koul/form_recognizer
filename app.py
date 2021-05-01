########### Python Form Recognizer Async Receipt #############

import pyrebase as pyrebase
from flask import Flask, jsonify, request
import json
import time
from requests import get, post

d = {}

config = {
    "apiKey": "AIzaSyApwm_OA6QKatzNVcYOuom7F0-gJ8Gtg6g",
    "authDomain": "trialapp-515fc.firebaseapp.com",
    "projectId": "trialapp-515fc",
    "storageBucket": "trialapp-515fc.appspot.com",
    "messagingSenderId": "106875930587",
    "appId": "1:106875930587:web:4be17c4b8882529a5dc9fe",
    "measurementId": "G-0PS6SE48G0",
    "databaseURL": ""
}


def download_img():
        firebase = pyrebase.initialize_app(config)

        storage = firebase.storage()

        storage.child('image/img.jpg').download('form.png')

def receipt(apim_key, post_url, data_bytes, headers, params):

        try:
            resp = post(url=post_url, data=data_bytes, headers=headers, params=params)
            if resp.status_code != 202:
                print("POST analyze failed:\n%s" % resp.text)
                quit()
            print("POST analyze succeeded:\n%s" % resp.headers)
            get_url = resp.headers["operation-location"]
        except Exception as e:
            print("POST analyze failed:\n%s" % str(e))
            quit()

        n_tries = 10
        n_try = 0
        wait_sec = 6
        while n_try < n_tries:
            try:
                resp = get(url=get_url, headers={"Ocp-Apim-Subscription-Key": apim_key})
                resp_json = json.loads(resp.text)
                if resp.status_code != 200:
                    print("GET Receipt results failed:\n%s" % resp_json)
                    quit()
                status = resp_json["status"]
                if status == "succeeded":
                    # print("Receipt Analysis succeeded:\n%s" % resp_json)
                    return resp_json
                    break
                if status == "failed":
                    print("Analysis failed:\n%s" % resp_json)
                    quit()
                # Analysis still running. Wait and retry.
                time.sleep(wait_sec)
                n_try += 1
            except Exception as e:
                msg = "GET analyze results failed:\n%s" % str(e)
                print(msg)
                quit()

import os
#
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.route('/', methods = ["GET"])
def hello_world():
    if request.method == 'GET':
        download_img()
        return {}

@app.route('/api', methods=["GET"])
def hello():
    if request.method == 'GET':
        endpoint = r"https://covidformrec.cognitiveservices.azure.com/"
        apim_key = "bdcfc1800c2f414d8f6a1c1e5d7566a3"
        source = r"form.png"

        headers = {
            # Request headers
            'Content-Type': 'image/png',
            'Ocp-Apim-Subscription-Key': apim_key,
        }

        params = {
            "includeTextDetails": True,
            "locale": "en-US"
        }

        with open(source, "rb") as f:
            data_bytes = f.read()


        post_url = endpoint + "/formrecognizer/v2.1-preview.2/prebuilt/businesscard/analyze"
        resp_json = receipt(apim_key, post_url, data_bytes, headers, params)
        resp_json = resp_json['analyzeResult']['documentResults'][0]['fields']['Emails']['valueArray'][0]

        d['email'] = resp_json['valueString']

        post_url = endpoint + "/formrecognizer/v2.1-preview.2/prebuilt/invoice/analyze"
        resp_json = receipt(apim_key, post_url, data_bytes, headers, params)

        # for name
        resp_json_temp = resp_json['analyzeResult']['documentResults'][0]['fields']['CustomerName']

        d['name'] = resp_json_temp['valueString']

        # # for ID
        # resp_json_temp = resp_json['analyzeResult']['documentResults'][0]['fields']['InvoiceId']
        #
        # d['id'] = resp_json_temp['text']

        # # for date
        # resp_json_temp = resp_json['analyzeResult']['documentResults'][0]['fields']['InvoiceDate']
        #
        # d['date'] = resp_json_temp['text']



        return d


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    # app.run()
    # app.run(host='127.0.0.1', port=8080, debug=True)

