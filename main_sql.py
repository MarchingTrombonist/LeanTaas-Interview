import pandas as pd
import sqlite3 as sqlite
import csv
from sqlite3 import Error
import os

connection = sqlite.connect("sqlite\Infusion.db")
cursor = connection.cursor()

# Importing; only needs to be done when changes are made in main.py
# df = pd.read_csv("Infusion_Fixed.csv")
# df.to_sql("Infusion", connection, if_exists="replace", index=True)


def executeSQL(sql):
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        print(row)


# cursor.execute("select * from Infusion")
# print(cursor.description)
executeSQL("""select * from Infusion where INPATIENT_DATA_ID_x = 'APTT014'""")
