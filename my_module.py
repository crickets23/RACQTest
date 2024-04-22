import sqlite3, sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
import os.path



        
db = ('DriverDemographics.csv','RACQ','Agecomparison',["id","Crash_Year","Crash_Police_Region","Crash_Severity","Involving_Male_Driver","Involving_Female_Driver" ,"Involving_Young_Driver_16-24","Involving_Senior_Driver_60plus","Involving_Provisional_Driver","Involving_Overseas_Licensed_Driver","Involving_Unlicensed_Driver","Count_Casualty_All"])


def csv_to_db(csv,db_name,table_name):
    con = sqlite3.connect(db_name +".db")
    cur = con.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?;",(table_name,))
    success = int(cur.fetchone()[0])    
    if success == 0:    
        engine = create_engine('sqlite:///' + db_name +'.db', echo=False)
        df = pd.read_csv(csv)
        with engine.connect() as connection:
            df.to_sql(
                name=table_name,
                con=connection,
                if_exists="replace"                
                )
    con.close()
    
def create_Demographics_tables():
    con = sqlite3.connect("RACQ.db")
    con.row_factory= sqlite3.Row
    cur = con.cursor()    
    

    cur.execute('''CREATE TABLE IF NOT EXISTS Agecomparison (
                                         "id" int,
                                         "Crash_Year" int,
                                         "Crash_Police_Region" VARCHAR(255),
                                         "Crash_Severity" VARCHAR(255),
                                         "Involving_Male_Driver" VARCHAR(255),
                                         "Involving_Female_Driver" VARCHAR(255),
                                         "Involving_Young_Driver_16-24" VARCHAR(255),
                                         "Involving_Senior_Driver_60plus" VARCHAR(255),
                                         "Involving_Provisional_Driver" VARCHAR(255),
                                         "Involving_Overseas_Licensed_Driver" VARCHAR(255),
                                         "Involving_Unlicensed_Driver" VARCHAR(255),
                                         "Count_Casualty_All" int);''')
    con.commit()
    con.close()



