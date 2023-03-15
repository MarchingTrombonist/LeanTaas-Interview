import pandas as pd
from datetime import datetime as dt

df = pd.read_csv("LeanTaaS_Infusion_Data_Analyst_Intern_Assignment.csv")

print(df.head())

print(df.iloc[:, 7:16])
# rename CHAIR_START to CHAIR_IN to match CHAIR_OUT
df = df.rename(columns={"CHAIR_START": "CHAIR_IN"})

# Convert all datetimes to %Y-%m-%d %H:%M

# dates
for col in ["CONTACT_DATE", "APPT_MADE_DATE", "APPT_CANC_DATE"]:
    df[col] = pd.to_datetime(df[col], infer_datetime_format=True).dt.strftime(
        "%Y-%m-%d"
    )

# times
for col in ["CHAIR_IN", "INFUSION_START", "INFUSION_END", "CHAIR_OUT"]:
    df[col] = pd.to_datetime(df[col], infer_datetime_format=True).dt.strftime("%H:%M")

# datetimes
for col in ["APPT_DTTM", "CHECKIN_DTTM", "CHECKOUT_DTTM"]:
    df[col] = pd.to_datetime(df[col], infer_datetime_format=True).dt.strftime(
        "%Y-%m-%d %H:%M"
    )

print(df.iloc[:, 7:16])
