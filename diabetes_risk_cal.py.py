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
import numpy as np
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


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
        requesturl = (
            self.server_url + "/Patient/" + patient_id + "$everything?_format=json"
        )
        return self.getJson(requesturl)["entry"]

    def getJson(self, requesturl):
        response = requests.get(
            requesturl, auth=(self.server_user, self.server_password)
        )
        response.raise_for_status()
        result = response.json()
        if self.debug:
            pprint(result)
        return result


client = SimpleFHIRClient(
    server_url="http://18.195.221.24", server_user="tutfhir", server_password="tutfhir1"
)


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

    pprint(
        "Patient record id = {}, Name = {}".format(
            patient_id, patient_given + " " + patient_family
        )
    )


hdl, sbp, bmi = [], [], []

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
    if all_data[i]["resource"]["resourceType"] == "Observation":
        observation_code = all_data[i]["resource"]["code"]["text"]

        if observation_code == "HDLc SerPl-mCnc":
            hdlvalue = all_data[i]["resource"]["valueQuantity"]["value"]
            hdl.append(hdlvalue)
            hdl_found = True

        elif observation_code == "Systolic blood pressure":
            sbpvalue = all_data[i]["resource"]["valueQuantity"]["value"]
            sbp.append(sbpvalue)
            sbp_found = True

        elif observation_code == "bmi":
            bmivalue = all_data[i]["resource"]["valueQuantity"]["value"]
            bmi.append(bmivalue)
            bmi_found = True


def calculateAge(born):

    # Calculating the age in years

    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def setGender(sex):
    return 1 if sex.lower() == "female" else 0


def calculateRisk(
    age,
    gender,
    ethnicity,
    family_history,
    fasting_glucose,
    sbp_value,
    hdl_value,
    bmi_value,
):

    sbp_value = sbp_value[-1]
    hdl_value = hdl_value[-1]
    bmi_value = bmi_value[-1]

    risk = 100 / (
        1
        + np.exp(
            -1
            * (
                (0.028 * age)
                + (0.661 * gender)
                + (0.412 * ethnicity)
                + (0.079 * fasting_glucose)
                + (0.018 * sbp_value)
                - (0.039 * hdl_value)
                + (0.07 * bmi_value)
                + (0.481 * family_history)
                - 13.415
            )
        )
    )
    return round(risk, 2)


# # Get missing data from user input

# ethnicity = int(input(
#         "Enter ethnicity (0 for non-Hispanic white, 1 for Latin American): "))
# family_history = int(input("Enter family history (0 if no, 1 if yes): "))
# fasting_glucose = float(input("Enter fasting glucose level in mg/dL: "))

# risk = calculateRisk(age, gender, ethnicity, family_history, fasting_glucose, sbp, hdl, bmi)

# pprint("7.5 year risk of Diabetes for the patient: {} %".format(risk))

FONT = ("Helvetica", 12)
TITLE_FONT = ("Helvetica", 12, "bold")
RESULT_FONT = ("Helvetica", 12, "bold", "yellow")

# window = tk.Tk()
window = ttk.Window("yeti")

# GUI main window creation part
style = ttk.Style()
style.configure("custom.TRadiobutton", foreground="white", font=FONT)
style.configure("Test.TLabel", background="yellow")

window.title("Diabetes Risk Calculator")
window.configure(background="white")
window.geometry("500x500")

# Create an entry field for patient ID
window_title = Label(window, text="Diabetes Risk Calculator", font=TITLE_FONT)
window_title.pack(pady=10)
id_label = Label(window, text="Enter Patient ID:", font=FONT)
id_label.place(relx=0.5, rely=0.3, anchor="center")  # Adjust the position
# Create an entry field for patient ID
id_entry = Entry(window)
id_entry.configure(font=FONT)
id_entry.place(relx=0.5, rely=0.4, anchor="center")  # Adjust the position

# Create a button to show input form
show_input_button = Button(
    window,
    text="ENTER",
    command=lambda: showInputForm(id_entry.get().strip(), hdl, sbp, bmi),
    font=FONT,
)
# show_input_button.pack(pady=10)
show_input_button.place(relx=0.5, rely=0.5, anchor="center")  # Adjust the position


def showInputForm(id_val, hdl=[], sbp=[], bmi=[]):
    # Create a new window for input form
    input_window_0 = Toplevel(window)
    input_window_0.title("Enter Risk Data")
    input_window_0.geometry("500x500")

    # Adjust content to the middle of the window
    input_window_0_title = Label(
        input_window_0, text="Enter Risk Data", font=TITLE_FONT
    )
    input_window_0_title.pack(pady=10)

    input_window = Frame(input_window_0)
    input_window.place(relx=0.5, rely=0.5, anchor="center")
    input_window.columnconfigure(0, weight=1)
    input_window.rowconfigure(0, weight=1)

    # Create radio buttons for ethnicity
    ethnicity_label = Label(input_window, text="Select ethnicity:")
    ethnicity_label.configure(font=FONT)
    ethnicity_label.pack()

    ethnicity_value = IntVar()
    ethnicity_frame = Frame(
        input_window
    )  # Create a separate frame for the radio buttons
    ethnicity_frame.pack()

    non_hispanic_white = Radiobutton(
        ethnicity_frame,
        text="Non-Hispanic White",
        variable=ethnicity_value,
        value=0,
    )
    non_hispanic_white.configure(font=FONT)
    non_hispanic_white.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    latin_american = Radiobutton(
        ethnicity_frame,
        text="Latin American",
        variable=ethnicity_value,
        value=1,
    )
    latin_american.configure(font=FONT)
    latin_american.grid(row=1, column=2, padx=10, pady=5, sticky="w")

    family_history_label = Label(input_window, text="Enter family history:")
    family_history_label.configure(font=FONT)
    family_history_label.pack()

    # Use IntVar to store the selected value
    family_history_var = IntVar()

    # Create radio buttons for family history
    family_history_frame = Frame(
        input_window
    )  # Create a separate frame for the radio buttons
    family_history_frame.pack()

    family_history_no = Radiobutton(
        family_history_frame,
        text="No",
        variable=family_history_var,
        value=0,
    )
    family_history_no.configure(font=FONT)
    family_history_no.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    family_history_yes = Radiobutton(
        family_history_frame,
        text="Yes",
        variable=family_history_var,
        value=1,
    )
    family_history_yes.configure(font=FONT)
    family_history_yes.grid(row=1, column=2, padx=10, pady=10, sticky="w")

    fasting_glucose_label = Label(
        input_window, text="Enter fasting glucose level in mg/dL:"
    )
    fasting_glucose_label.configure(font=FONT)
    fasting_glucose_label.pack()
    fasting_glucose_entry = Entry(input_window)
    fasting_glucose_entry.configure(font=FONT)
    fasting_glucose_entry.pack(pady=20)

    # Button to calculate risk
    calculate_risk_button = Button(
        input_window,
        text="CALCULATE RISK",
        font=FONT,
        command=lambda: showRisk(
            id_val,
            all_patients,
            sbp,
            hdl,
            bmi,
            ethnicity_value.get(),
            family_history_var.get(),
            fasting_glucose_entry.get(),
            input_window,
        ),
    )

    calculate_risk_button.pack(pady=20)


def showRisk(
    id_val,
    all_patients,
    sbp,
    hdl,
    bmi,
    ethnicity,
    family_history,
    fasting_glucose,
    input_window,
):
    try:
        sex = all_patients[id_list.index(id_val)]["gender"]
        gender = setGender(sex)
        born = datetime.strptime(
            all_patients[id_list.index(id_val)]["birthDate"], "%Y-%m-%d"
        )
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
    risk = calculateRisk(
        age, gender, ethnicity, family_history, fasting_glucose, sbp, hdl, bmi
    )

    # Show risk and observation information in a new window
    result_window_0 = Toplevel(input_window)
    result_window_0.title("Risk result")
    result_window_0.geometry("500x500")

    result_window_0_title = Label(result_window_0, text="Risk result", font=TITLE_FONT)
    result_window_0_title.pack(pady=10)
    result_window = Frame(result_window_0)
    result_window.place(relx=0.5, rely=0.5, anchor="center")

    Label(
        result_window,
        text="HDL value for the patient: {} mg/dL".format(hdl[-1]),
        pady=5,
        font=FONT,
    ).pack()
    Label(
        result_window,
        text="SBP value for the patient: {} mm[Hg]".format(sbp[-1]),
        pady=5,
        font=FONT,
    ).pack()
    Label(
        result_window,
        text="BMI value for the patient: {} kg/m2".format(bmi[-1]),
        pady=5,
        font=FONT,
    ).pack()

    result = ttk.Label(
        result_window,
        text=f"7.5 year risk of Diabetes for the patient: {risk} %",
        font=FONT,
    )
    result_style = ttk.Style()
    result_style.configure(
        "Test.TLabel", background="#ffbf00"
    )  # Set the background color

    result.configure(style="Test.TLabel")
    result.pack(pady=10)

    # Add a button to return to the initial Toplevel window
    Button(
        result_window,
        text="Return to Input Window",
        font=FONT,
        command=result_window_0.destroy,
    ).pack(pady=10)


# def destroy_windows(window1, window2):
#     window1.destroy()
#     window2.destroy()

window.mainloop()
