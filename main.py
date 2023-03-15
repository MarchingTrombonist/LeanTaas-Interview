import numpy as np
import pandas as pd

df = pd.read_csv("LeanTaaS_Infusion_Data_Analyst_Intern_Assignment.csv")
# print(df)

for colName in df.iloc[:, 3:].columns.values:
    print(colName + ": ", end="")
    print(df[colName].unique())
