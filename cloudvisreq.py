from base64 import b64encode
import os
from os.path import *
from sys import argv, exit
import json
import requests

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
RESULTS_DIR = 'jsons'
if (os.path.exists(RESULTS_DIR) == 0):
    os.makedirs(RESULTS_DIR)

def make_image_data_list(image_filenames):
    """
    image_filenames is a list of filename strings
    Returns a list of dicts formatted as the Vision API needs them to be
    """
    img_requests = []
    for imgname in image_filenames:
        with open(imgname, "rb") as f:
            ctxt = b64encode(f.read()).decode()
            img_requests.append({ 'image': {'content': ctxt}, 
                    'features': [{'type': 'TEXT_DETECTION', 'maxResults': 1}] })
    return img_requests


def make_image_data(image_filenames):
    """Returns the image data lists as bytes"""
    imgdict = make_image_data_list(image_filenames)
    return json.dumps({"requests": imgdict }).encode()


def request_ocr(api_key, image_filenames):
    response = requests.post(ENDPOINT_URL,
            data=make_image_data(image_filenames),
            params={'key': api_key},
            headers={'Content-Type': 'application/json'})
    return response


if __name__ == '__main__':

    if (len(argv) > 2):
        api_key = argv[1]
        image_filenames = argv[2:]
    else:
        error_msg = "Please supply an api key, then one or more image filenames\n" + \
                    "$ python cloudvisreq.py api_key image1.jpg image2.jpg ..."
        exit(error_msg)

    response = request_ocr(api_key, image_filenames)
    if response.status_code != 200 or response.json().get('error'):
        print(response.text)
    else:
        for idx, resp in enumerate(response.json()['responses']):
            # save to JSON file
            imgname = image_filenames[idx].split('.')[0]
            jpath = join(RESULTS_DIR, basename(imgname) + '.json')
            with open(jpath, 'w') as f:
                datatxt = json.dumps(resp, indent=2)
                print "Wrote %d bytes to %s" % (len(datatxt), jpath)
                f.write(datatxt)
    
            t = resp['textAnnotations'][0]
            print(t['description'])
