import os
import openai
import requests
import pandas as pd
import numpy as np
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
# openai.api_key = os.getenv("OPENAI_API_KEY")

print(openai.api_key)
Drug = pd.read_csv('resources/Drug_clean.csv')


# Retrieve Symptoms List from Dataset
def retrieveSymptomsList():
    for i in range(Drug.shape[0]):
        Drug.loc[i, 'Condition'] = Drug.loc[i, 'Condition'].capitalize()

    Data_grouped_condition = Drug.groupby(['Condition'])
    Data_grouped_condition.describe().head()
    condition_list = list(Data_grouped_condition.groups.keys())
    return condition_list


# Use OPENAI API to extract symptoms from user's input
# @app.route("/", methods=("GET", "POST"))
# def index():
#     if request.method == "POST":
#         condition_list = retrieveSymptomsList()
#         #print(condition_list)
#         feel_input = request.form["feel_input"]
#         response = openai.Completion.create(
#             model="text-davinci-003",
#             prompt=generate_prompt(feel_input, condition_list),
#             temperature=0.6,
#         )
#         return redirect(url_for("index", result=response.choices[0].text))
#
#     result = request.args.get("result")
#     print(result)
#     return render_template("index.html", result=result)

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        condition_list = retrieveSymptomsList()
        # print(condition_list)
        feel_input = request.form["feel_input"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(feel_input, condition_list),
            temperature=0,
        )
        extracted_symptoms = parse_response(response.choices[0].text)
        found_drugs = recommend_drugs(extracted_symptoms)
        print(extracted_symptoms)
        sym, symptoms_str = response.choices[0].text.split("Symptoms: ")
        # print(sort_by_effective(found_drugs))
        # sort_by_effective(found_drugs)
        # print(extracted_symptoms)
        return redirect(url_for("index", symptoms=symptoms_str))

    result = request.args.get("result")
    return render_template("index.html", result=result)

def parse_response(response_text):
    # Extract the symptoms portion of the line
    symptoms = response_text.replace("Symptoms: ", "").strip()
    print(symptoms)
    # Split the symptoms by commas and remove any leading/trailing spaces
    symptom_list = [symptom.strip() for symptom in symptoms.split(", ")]
    return symptom_list

    return []  # Return an empty list if no symptoms were found in the response


def generate_prompt(feel_input, condition_list):
    prompt_input = f"""
    Your task is to extract a symptom or list of symptoms from a user's input.
    
    From the user's input below, delimited by triple quotes, extract a list of symptoms that the user may experience.
    Limit the extracted symptoms to those provided in the symptoms list below.
    Print the extracted symptoms in the following format:
    Symptoms: symptom1, symptom2
    
    Symptoms List: ```{condition_list}```
    
    User's Input: ```{feel_input}```
    """
    return prompt_input

    # response = get_completion(prompt)
    # print(response)


def recommend_drugs(symptoms_list):
    recommended_drugs = []

    for symptom in symptoms_list:
        drugs_for_one = []
        for i in range(len(Drug)):
            if symptom in Drug.loc[i, 'Condition']:
                drugs_for_one.append(Drug.loc[i])
        # Sort the drugs by satisfaction level and select top 5
        drugs_for_one.sort(key=lambda drug: drug['Satisfaction'], reverse=True)
        drugs_for_one = drugs_for_one[:5]
        recommended_drugs.append(drugs_for_one)
    return recommended_drugs


def sort_by_effective(recommended_drugs):
    effective_sorted_list = []
    for sublist in recommended_drugs:
        sorted_sublist = sorted(sublist, key=lambda x: x["Effective"], reverse=True)
        effective_sorted_list.append(sorted_sublist)

    return effective_sorted_list

