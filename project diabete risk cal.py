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


def calculateAge(born):
    """
    Calculating the age in years
    """
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < 
                                     (born.month, born.day))

def calculateRisk(age, gender, family_history, glucose, sbp, hdl):
    """
    Calculate the diabetes risk level 
    """
    risk = 100 / (1 + np.exp(-1 * ((0.028 * age) + (0.661 * sex) + (0.412 * ethnicity) +
                                    (0.079 * fasting_glucose) + (0.018 * sbp) - (0.039 * hdl) +
                                    (0.07 * bmi) + (0.481 * family_history) - 13.415)))
    return risk

def retrievePatientData():
    # Get all the record data from the database for the given patient
    patient_id = patient_id_entry.get()
    patient_data = client.getPatientData(patient_id)





