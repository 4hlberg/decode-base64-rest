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

def filenamegenerate(d_filename):
    decodedfilename = d_filename + ".jpeg"
    return decodedfilename

def image_data(img_base64):
    img_data =img_base64
    return img_data

class DataAccess:
    def __get_image_data(self, image):
        logger.info("Fetching data from file: %s")
        img_base64 = str()
        for k, v in image.items():
            if k == 'image':
                img_base64 += v
                image_data(img_base64)

        else:
            pass
        return img_base64.image()


    def __get_all_decodees(self, name):
        logger.info("Fetching data from file: %s")
        d_filename = str()
        for k, v in name.items():
            if k == 'name':
                d_filename += v
            elif k == 'employee-number':
                d_filename += v
        else:
            pass
        return filenamegenerate(d_filename)


    def get_decode(self, path):
        print('getting all decodees')
        return self.__get_all_decodees(path)

    def get_img_data(self, path):
        print("Getting image data")
        return self.__get_image_data(path)

data_access_layer = DataAccess()

@app.route("/<path:path>", methods=["GET"])
def path():
    json_data = json.load(open(path))
    for entity in json_data:
        decodedfilename = data_access_layer.get_decode(entity)
        img_data = data_access_layer.get_img_data(entity)
        with open(app.root_path + "/" + decodedfilename, 'wb') as fh:
            fh.write(base64.b64decode(img_data))

    return Response(
        print("foo"),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True, port=os.environ.get('port',5000))
