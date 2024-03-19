# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 16:26:38 2024

@author: chees
"""

import json
from datetime import date, datetime
import requests
from pprint import pprint
from tkinter import *
import PIL
from PIL import Image, ImageTk
from tkinter import ttk

class SimpleFHIRClient(object):
    def __init__(self, server_url, server_user, server_password, debug=False):
        self.debug = debug
        self.server_url = server_url
        self.server_user = server_user
        self.server_password = server_password

    def getAllPatients(self):
        requesturl = self.server_url + "/Patient?_format=json"
        entries = self.getJson(requesturl)["entry"]
        return [entry["resource"] for entry in entries]

    def getAllDataForPatient(self, patient_id):
        requesturl = self.server_url + "/Patient/" + \
            patient_id + "$everything?_format=json"
        return self.getJson(requesturl)["entry"]

    def getJson(self, requesturl):
        response = requests.get(requesturl,
                                auth=(self.server_user, self.server_password))
        response.raise_for_status()
        result = response.json()
        if self.debug:
            pprint(result)
        return result


client = SimpleFHIRClient(
    server_url="http://tutsgnfhir.com",
    server_user="tutfhir",
    server_password="tutfhir1")


"""

Project App GUI starts from here

"""

# Get all patients
all_patients = client.getAllPatients()

# Get all the data for ONE patient, e.g. for the first one; Python indexing starts from 0.
first_patient_all = client.getAllDataForPatient(all_patients[0]["id"])
#pprint(first_patient_all)

