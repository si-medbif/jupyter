#!/usr/bin/python3

import requests
import json
import re
from google.cloud import storage
import os
import sys

def loadgdc(file_name):
    ids = []
    names = []
    with open(file_name,'r') as infile:
        for i in infile:
            ids.append(i.strip().split("\t")[0])
            names.append(i.strip().split("\t")[1])
    return([ids[1:],names[1:]])

def getsvs(file_id,file_name):
    data_endpt = "https://api.gdc.cancer.gov/data/{}".format(file_id)
    with open(file_name, "wb") as f:
        print("Downloading %s" % file_name)
        response = requests.get(data_endpt, stream=True)
        total_length = response.headers.get('content-length')

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
    print("\n%s is uploaded to google bucket.\n" % file_name)

    
if __name__ == '__main__':
    filelst = loadgdc(sys.argv[1])
    for i in range(len(filelst[0])):
        file_id = filelst[0][i]
        file_name = filelst[1][i]
        getsvs(file_id,file_name)
        to_gbucket(file_name,'nci-test')  
  
