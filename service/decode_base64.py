from flask import Flask, request, Response
import os
import requests
import logging
import json
import dotdictify
from time import sleep
import base64


app = Flask(__name__)
logger = None
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger('decode-base64-service')

# Log to stdout
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter(format_string))
logger.addHandler(stdout_handler)
logger.setLevel(logging.DEBUG)

headers = {}
if os.environ.get('headers') is not None:
    headers = json.loads(os.environ.get('headers').replace("'","\""))

def decode(v):
    for key, value in v.items():
        if isinstance(value,dict):
            encode(value)
        else:
            v[key] = base64.b64decode(requests.get(value).content).decode("utf-8")

    return v

def transform(obj):
    res = {}
    # print(obj.items())
    for k, v in obj.items():
        if k == "image":
            if dotdictify.dotdictify(v).image is not None:
                logger.info("Decoding images from url to base64...")
                res[k] = decode(v)

            else:
                pass
        try:
            _ = json.dumps(v)
        except Exception:
            pass
        else:
            res[k] = v
    return res

class DataAccess:

    def __get_all_users(self, path):
        logger.info("Fetching data from url: %s", path)
        offset = 0
        limit = 5
        page_number = 1
        url= path + "&limit=" + str(limit) + "&offset=" + str(offset)

        req = requests.get(url, headers=headers)
        if req.status_code != 200:
            logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
            raise AssertionError("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
        clean = json.loads(req.text)

        for offset in range(0, offset, len(req.headers['Content-Range'])):
            yield transform(clean)
            print(count)
            last_offset = page_number * limit
            print('last offset =', last_offset)
            page_number +=1

    def get_users(self, path):
        print("Getting all users")
        return self.__get_all_users(path)

data_access_layer = DataAccess()

@app.route("/decode", methods=["GET"])
def get_decoding():
    path = os.environ.get("decode_base_url") + os.environ.get("decode_region")
    json_data = data_access_layer.get_users(path)
    for entity in json_data:
        decodedfilename = entity['rogaland-image-decode:name'].replace(" ", "_") + "_" +entity['rogaland-image-decode:employee-number'] + ".jpeg"
                #img_data = data_access_layer.get_users(json_data.image)
        if entity['rogaland-image-decode:image'] is not None:
            with open(app.root_path + "/" + decodedfilename, 'wb') as fh:
                fh.write(base64.b64decode(entity['rogaland-image-decode:image']))
        else:
            pass
    return Response(
        print("foo"),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True, port=os.environ.get('port',5000))
