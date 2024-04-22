from flask import Flask, render_template,request,url_for,session, redirect
import sqlite3, json, plotly, csv, sqlalchemy
from datetime import datetime
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import smtplib
import my_module
import json
import os

def load_language_file(filename):
    with open(f'languages/{filename}', 'r', encoding='utf-8') as file:
        return json.load(file)

languages = {
    'en': load_language_file('en.json'),
    'es': load_language_file('es.json'),
    'fr': load_language_file('fr.json'),
}



app = Flask(__name__)
app.secret_key = os.urandom(24)  # or any other secure way to generate a random secret key

@app.route('/switch_lang', methods=['GET', 'POST'])
def switch_lang():
    lang = request.form.get('lang')
    print(f"Selected language: {lang}")  # Add this print statement
    if lang is not None and lang != session.get('lang'):
        session['lang'] = lang
        print(session)  # Add this print statement to check the session
    return redirect(request.referrer)




@app.route('/', methods=["GET","POST"])
def home():
    lang = session.get('lang', 'en')
    strings = languages[lang]
    return render_template("home.html", strings=strings)




@app.route('/info', methods=["GET","POST"])
def info():
    lang = session.get('lang', 'en')
    strings = languages[lang]
    my_module.csv_to_db("DriverDemographics.csv", "RACQ", "Agecomparison")
    con = sqlite3.connect("RACQ.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    headers = []
    cols = []
    message = None
    if request.method == "POST":
        if request.form['go'] == 'Filter':
            age = request.form["age"]
            sex = request.form["sex"]
            license_type = request.form["license_type"]
            if not (age and sex and license_type):
                message = "Please select your age, sex and license type."
            else:
                cur.execute('''
                SELECT
                COUNT(CASE WHEN "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Provisional_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes' THEN 1 END) AS "16-24 male - provisional",
                COUNT(CASE WHEN "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Provisional_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes' THEN 1 END) AS "16-24 female - provisional",
                COUNT(CASE WHEN "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Provisional_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes' THEN 1 END) AS "60+ male - provisional",
                COUNT(CASE WHEN "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Provisional_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes' THEN 1 END) AS "60+ female - provisional",
                COUNT(CASE WHEN "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Overseas_Licensed_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes' THEN 1 END) AS "16-24 male - overseas",
                COUNT(CASE WHEN "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Overseas_Licensed_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes' THEN 1 END) AS "16-24 female - overseas",
                COUNT(CASE WHEN "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Overseas_Licensed_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes' THEN 1 END) AS "60+ male - overseas",
                COUNT(CASE WHEN "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Overseas_Licensed_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes' THEN 1 END) AS "60+ female - overseas",
                COUNT(CASE WHEN "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Unlicensed_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes' THEN 1 END) AS "16-24 male - no license",
                COUNT(CASE WHEN "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Unlicensed_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes' THEN 1 END) AS "16-24 female - no license",
                COUNT(CASE WHEN "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Unlicensed_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes' THEN 1 END) AS "60+ male - no license",
                COUNT(CASE WHEN "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Unlicensed_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes' THEN 1 END) AS "60+ female - no license"
                FROM Agecomparison;
                ''')
                cols = cur.fetchall()
                headers = [desc[0] for desc in cur.description]
                # Convert the result to a dictionary
                data = dict(zip(headers, cols[0]))

                # Create a bar chart
                fig = px.bar(x=list(data.keys()), y=list(data.values()), labels={'x':'Category', 'y':'Count'})

                if fig is not None:
                    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                else:
                    graphJSON = None

                if age == ("16-24") and license_type == ("Provisional") and sex == ("Male"):
                    cur.execute('''
                        SELECT COUNT(*) AS "Here is the number of crashes caused by 16-24 year old males with a provisional license:"
                        FROM Agecomparison
                        WHERE "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Provisional_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                    ############################################################################
                if age == ("16-24") and license_type == ("Provisional") and sex == ("Female"):
                    cur.execute('''
                        SELECT COUNT(*) AS "Here is the number of crashes caused by 16-24 year old females with a provisional license:"
                        FROM Agecomparison
                        WHERE "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Provisional_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                    ##########################################################################
                if age == ("60+") and license_type == ("Provisional") and sex == ("Male"):
                    cur.execute('''
                        SELECT COUNT(*) AS "Here is the number of crashes caused by 60+ year old males with a provisional license:"
                        FROM Agecomparison
                        WHERE "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Provisional_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                    ############################################################################
                if age == ("60+") and license_type == ("Provisional") and sex == ("Female"):
                    cur.execute('''
                        SELECT COUNT(*) AS "Here is the number of crashes caused by 60+ year old females with a provisional license:"
                        FROM Agecomparison
                        WHERE "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Provisional_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                #############################################################################################
                if age == ("16-24") and license_type == ("Overseas License") and sex == ("Male"):
                    cur.execute('''
                        SELECT COUNT(*) AS "Here is the number of crashes caused by 16-24 year old males with an overseas license:"
                        FROM Agecomparison
                        WHERE "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Overseas_Licensed_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                    ############################################################################
                if age == ("16-24") and license_type == ("Overseas License") and sex == ("Female"):
                    cur.execute('''
                        SELECT COUNT(*) AS "Here is the number of crashes caused by 16-24 year old females with a overseas license:"
                        FROM Agecomparison
                        WHERE "Involving_Young_Driver_16-24" = 'Yes' AND "Involving_Overseas_Licensed_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                #############################################################################################
                if age == ("60+") and license_type == ("Overseas License") and sex == ("Male"):
                    cur.execute('''
                        SELECT COUNT(*) AS "Here is the number of crashes caused by 60+ year old males with an overseas license:"
                        FROM Agecomparison
                        WHERE "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Overseas_Licensed_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                if age == ("60+") and license_type == ("Overseas License") and sex == ("Female"):
                    cur.execute('''
                        SELECT COUNT('Yes') AS "Here is the number of crashes caused by 60+ year old females with an overseas license:"
                        FROM Agecomparison
                        WHERE "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Overseas_Licensed_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                    ##########################################################################
                if age == ("60+") and license_type == ("No License") and sex == ("Male"):
                    cur.execute('''
                        SELECT COUNT('*') AS "Here is the number of crashes caused by 60+ year old males with no license:"
                        FROM Agecomparison
                        WHERE "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Unlicensed_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                ################################################################################
                if age == ("60+") and license_type == ("No License") and sex == ("Female"):
                    cur.execute('''
                        SELECT COUNT('*') AS "Here is the number of crashes caused by 60+ year old females with no license:"
                        FROM Agecomparison
                        WHERE "Involving_Senior_Driver_60plus" = 'Yes' AND "Involving_Unlicensed_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()

                if age == ("16-24") and license_type == ("No License") and sex == ("Male"):
                    cur.execute('''
                        SELECT COUNT('*') AS "Here is the number of crashes caused by 16-24 year old males with no license:"
                        FROM Agecomparison
                        WHERE "Involving_Young_Driver_16" = 'Yes' AND "Involving_Unlicensed_Driver" = 'Yes' AND "Involving_Male_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
                ################################################################################
                if age == ("16-24") and license_type == ("No License") and sex == ("Female"):
                    cur.execute('''
                        SELECT COUNT('*') AS "Here is the number of crashes caused by 16-24 year old males with no license:"
                        FROM Agecomparison
                        WHERE "Involving_Young_Driver_16" = 'Yes' AND "Involving_Unlicensed_Driver" = 'Yes' AND "Involving_Female_Driver" = 'Yes'
                        ;
                    ''')
                    cols = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    con.close()
            

            con.close()

        return render_template('info.html', headers=headers, cols=cols, message = message, graphJSON = graphJSON, strings=strings)
    return render_template('info.html')

if __name__ == '__main__':
    app.run(use_reloader=False,debug=True)
 