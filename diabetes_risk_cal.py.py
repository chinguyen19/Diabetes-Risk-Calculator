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
import numpy as np

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
    server_url="http://18.195.221.24",
    server_user="tutfhir",
    server_password="tutfhir1")


"""

Project App GUI starts from here

"""

# Get all patients
all_patients = client.getAllPatients()

# Lists for all the names and patient id's
pprint("The names and id's for all the {} patients...".format(len(all_patients)))
print("")

id_list = []
name_list = [] 

for patient_record in all_patients:
    patient_id = patient_record["id"]
    patient_family = patient_record["name"][0]["family"][0]
    patient_given = patient_record["name"][0]["given"][0]

    id_list.append(patient_id)
    name_list.append(patient_given + " " + patient_family)
    
    pprint("Patient record id = {}, Name = {}".format(patient_id, patient_given + " " + patient_family))


hdl = []
sbp = []
bmi = []

# Fetching all the data for the patient
id_val = input("Enter the patient ID: ")
all_data = client.getAllDataForPatient(all_patients[id_list.index(id_val)]["id"])
    
# Extract only the desired observations (variables)
x = range(0, len(all_data))
hdl_found = False
sbp_found = False
bmi_found = False
    
    # Find all observations among 
for i in x:
    if all_data[i]['resource']['resourceType'] == 'Observation':
        observation_code = all_data[i]['resource']['code']['text']
        
        if observation_code == "HDLc SerPl-mCnc":
            hdlvalue = all_data[i]['resource']['valueQuantity']['value']        
            hdl.append(hdlvalue)
            hdl_found = True
        
        
        elif observation_code == "Systolic blood pressure":
            sbpvalue = all_data[i]['resource']['valueQuantity']['value']                 
            sbp.append(sbpvalue)
            sbp_found = True
            
        
        elif observation_code == "bmi":
            bmivalue = all_data[i]['resource']['valueQuantity']['value']                   
            bmi.append(bmivalue)
            bmi_found = True
            
# Check if observations were found
if not hdl_found:
    print("HDL Cholesterol value not found.")
else:
    pprint("HDL value for the patient: {} mg/dL".format(hdl[-1]))
if not sbp_found:
    print("Systolic Blood Pressure value not found.")
else:
    pprint("SBP value for the patient: {} mm[Hg]".format(sbp[-1]))
if not bmi_found:
    print("BMI value not found.")        
else:
     pprint("BMI value for the patient: {} kg/m2".format(bmi[-1]))      



def calculateAge(born):
    
    # Calculating the age in years
    
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < 
                                     (born.month, born.day))

def calculateRisk(age, gender, family_history, fasting_glucose, sbp, hdl, bmi):
    

    
    # Fetch gender data here
    """
    Write your code here
    """
    
   
    
    risk = 100 / (1 + np.exp(-1 * ((0.028 * age) + (0.661 * gender) + (0.412 * ethnicity) +
                                    (0.079 * fasting_glucose) + (0.018 * sbp) - (0.039 * hdl) +
                                    (0.07 * bmi) + (0.481 * family_history) - 13.415)))
    return round(risk, 2)




born = datetime.strptime(all_patients[id_list.index(id_val)]['birthDate'], '%Y-%m-%d')
age = calculateAge(born)
# Assume user input
fasting_glucose = 90 # This we can try random number, in which 70-100 mg/dL is normal range indicite stable blood sugar level
family_history = 0
ethnicity = 1
gender = 1

risk = calculateRisk(age, gender, family_history, fasting_glucose, sbp[-1], hdl[-1], bmi[-1])
pprint("7.5 year risk of Diabetes for the patient: {} %".format(risk))