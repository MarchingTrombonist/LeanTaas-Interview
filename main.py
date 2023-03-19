import pandas as pd

df = pd.read_csv("LeanTaaS_Infusion_Data_Analyst_Intern_Assignment.csv")

# print(df.head())

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


# Add Notes column; move notes from descriptions
dfSplit = df["ORDER_DESCRIPTION"].str.split("\n", n=1, expand=True)
df["ORDER_DESCRIPTION"] = dfSplit[0]
df.insert(17, "ORDER_NOTES", dfSplit[1])


# Fix 11/4 extra column (column 20)
badRows = df[~df.iloc[:, 20].isna()].index
for colNum in range(18, 20):
    df.iloc[badRows, colNum] = df.iloc[badRows, colNum + 1]

df = df.iloc[:, ~df.columns.str.match("Unnamed")]
