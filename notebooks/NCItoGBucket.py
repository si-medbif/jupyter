#!/usr/bin/python3

import requests
import json
import re
from google.cloud import storage
import os
import sys
from binascii import b2a_base64
import time

def lst_bucket(bucket_name):
    res = []
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs()
    for blob in blobs:
        res.append(blob.name)
    return(res)

def blob_md5(bucket_name, blob_name):
    """Prints out a blob's metadata."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    return(blob.md5_hash)

def loadgdc_json(file_name):
    with open(file_name) as json_file:  
        data = json.load(json_file)
    return(data)

def md5process(file_md5):
    b64 = b2a_base64(bytes.fromhex(file_md5))
    b64 = str(b64.decode('utf-8').rstrip())
    return(b64)

def getsvs(file_id,file_name):
    data_endpt = "https://api.gdc.cancer.gov/data/{}".format(file_id)
    with open(file_name, "wb") as f:
        print("Downloading %s" % file_name)
        response = requests.get(data_endpt, stream=True)
        total_length = response.headers.get('content-length')
        print(total_length)

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                sys.stdout.flush()

def to_gbucket(file_name, bucket):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    os.remove(file_name)
    print("%s is uploaded to google bucket." % file_name)

    
if __name__ == '__main__':
    '''USAGE: python3 NCItoGBucket.py gdc_meta_data.json google-bucket-name '''
    filelst = loadgdc_json(sys.argv[1]) #gdc_meta_data.json
    bucket = sys.argv[2] #google-bucket-name
    exist = lst_bucket(bucket)
    i = 0
    while i < len(filelst):
        print(i)
        t_filelst = filelst[i]
        file_id = t_filelst['file_id']
        file_name = t_filelst['file_name']
        file_md5 = md5process(t_filelst['md5sum'])
        if file_name not in exist:
            try:
                getsvs(file_id,file_name)
                to_gbucket(file_name,bucket)
                #i += 1 #Comment out to check md5sum of the newly uploaded file
                exist = lst_bucket(bucket)
            except:
                time.sleep(30) #Try reconnecting in 30s
        elif file_md5 != str(blob_md5(bucket, file_name)):
            try:
                getsvs(file_id,file_name)
                to_gbucket(file_name,bucket)
                #i += 1 #Comment out to check md5sum of the newly uploaded file
            except:
                time.sleep(30) #Try reconnecting in 30s
        else:
            i += 1
