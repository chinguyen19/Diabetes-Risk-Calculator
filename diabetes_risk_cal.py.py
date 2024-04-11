
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
import tkinter as tk
from tkinter import messagebox

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


hdl, sbp, bmi = [],[],[]

# Fetching all the data for the patient
id_val = input("Enter the patient ID: ")
all_data = client.getAllDataForPatient(all_patients[id_list.index(id_val)]["id"])
    
# Extract only the desired observations (variables)
x = range(0, len(all_data))
hdl_found = False
sbp_found = False
bmi_found = False
    
# Find certain observations (hdl, sbp, bmi) from the fhir database 
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
            

def calculateAge(born):
    
    # Calculating the age in years
    
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < 
                                     (born.month, born.day))

def setGender(sex):
    return 1 if sex.lower() == "female" else 0

def calculateRisk(age, gender, ethnicity, family_history, fasting_glucose, sbp_value, hdl_value, bmi_value):
   
    sbp_value = sbp_value[-1]
    hdl_value = hdl_value[-1]
    bmi_value = bmi_value[-1] 

    risk = 100 / (1 + np.exp(-1 * ((0.028 * age) + (0.661 * gender) + (0.412 * ethnicity) +
                                    (0.079 * fasting_glucose) + (0.018 * sbp_value) - (0.039 * hdl_value) +
                                    (0.07 * bmi_value) + (0.481 * family_history) - 13.415)))
    return round(risk, 2)



# # Get missing data from user input

# ethnicity = int(input(
#         "Enter ethnicity (0 for non-Hispanic white, 1 for Latin American): "))
# family_history = int(input("Enter family history (0 if no, 1 if yes): "))
# fasting_glucose = float(input("Enter fasting glucose level in mg/dL: "))

# risk = calculateRisk(age, gender, ethnicity, family_history, fasting_glucose, sbp, hdl, bmi)

# pprint("7.5 year risk of Diabetes for the patient: {} %".format(risk))


def showInputForm(id_val, hdl=[], sbp=[], bmi=[]):
    # Create a new window for input form
    input_window = Toplevel(window)
    input_window.title("Enter Risk Data")
    input_window.geometry("300x250")
    
    # Create entry fields for additional input
    ethnicity_label = Label(input_window, text="Enter ethnicity (0 for non-Hispanic white, 1 for Latin American):")
    ethnicity_label.pack()
    ethnicity_entry = Entry(input_window)
    ethnicity_entry.pack()
    
    family_history_label = Label(input_window, text="Enter family history (0 if no, 1 if yes):")
    family_history_label.pack()
    family_history_entry = Entry(input_window)
    family_history_entry.pack()
    
    fasting_glucose_label = Label(input_window, text="Enter fasting glucose level in mg/dL:")
    fasting_glucose_label.pack()
    fasting_glucose_entry = Entry(input_window)
    fasting_glucose_entry.pack()
    
    # Button to calculate risk
    calculate_risk_button = Button(input_window, text="Calculate Risk",
                                   command=lambda: showRisk(id_val, all_patients, sbp, hdl, bmi,
                                                            ethnicity_entry.get(), family_history_entry.get(),
                                                            fasting_glucose_entry.get(), input_window))
    calculate_risk_button.pack(pady=20)    


def showRisk(id_val, all_patients, sbp, hdl, bmi, ethnicity, family_history, fasting_glucose, input_window):
    try:
        sex = all_patients[id_list.index(id_val)]['gender']
        gender = setGender(sex)
        born = datetime.strptime(all_patients[id_list.index(id_val)]['birthDate'], '%Y-%m-%d')
        age = calculateAge(born)
    except IndexError:
        messagebox.showerror("Error", "Patient ID not found")
        return

    # Convert input values to appropriate types
    ethnicity = int(ethnicity)
    family_history = int(family_history)
    fasting_glucose = float(fasting_glucose)

    # Check if any of the observations are missing
    if not sbp or not hdl or not bmi:
        messagebox.showerror("Missing Data", "Please take complementary tests.")
        return

    # Calculate risk
    risk = calculateRisk(age, gender, ethnicity, family_history, fasting_glucose, sbp, hdl, bmi)

    # Show risk and observation information in a new window
    result_window = Toplevel(input_window)
    result_window.title("Risk result")
    Label(result_window, text="HDL value for the patient: {} mg/dL".format(hdl[-1]), pady=5).pack()
    Label(result_window, text="SBP value for the patient: {} mm[Hg]".format(sbp[-1]), pady=5).pack()
    Label(result_window, text="BMI value for the patient: {} kg/m2".format(bmi[-1]), pady=5).pack()
    Label(result_window, text=f'7.5 year risk of Diabetes for the patient: {risk} %', pady=10, bg='#ffbf00').pack()


# GUI main window creation part
window = tk.Tk()
window.title("Diabetes Risk Calculator")
window.configure(background="white")
window.geometry("370x250")

# Create an entry field for patient ID
id_label = Label(window, text="Enter Patient ID:")
id_label.pack()
# Create an entry field for patient ID
id_entry = Entry(window)
id_entry.pack()

# Create a button to show input form
show_input_button = Button(window, text="Enter", command=lambda: showInputForm(id_entry.get().strip(), hdl, sbp, bmi))
show_input_button.pack(pady=10)

window.mainloop()
