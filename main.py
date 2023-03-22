import pandas as pd
import numpy as np

df = pd.read_csv("LeanTaaS_Infusion_Data_Analyst_Intern_Assignment.csv")

# rename CHAIR_START to CHAIR_IN to match CHAIR_OUT
df = df.rename(columns={"CHAIR_START": "CHAIR_IN"})


# Add Notes column; move notes from descriptions
dfSplit = df["ORDER_DESCRIPTION"].str.split("\n", n=1, expand=True)
df["ORDER_DESCRIPTION"] = dfSplit[0]
df.insert(17, "ORDER_NOTES", dfSplit[1])

# Fix 11/4 extra column (column 20)
badRows = df[~df.iloc[:, 20].isna()].index
for colNum in range(18, 20):
    df.iloc[badRows, colNum] = df.iloc[badRows, colNum + 1]

df = df.iloc[:, ~df.columns.str.match("Unnamed")]

# Convert all datetimes to the same format
# Make all times datetimes using the checkin

# dates
for col in ["CONTACT_DATE", "APPT_MADE_DATE", "APPT_CANC_DATE"]:
    df[col] = pd.to_datetime(df[col], infer_datetime_format=True).dt.strftime(
        "%Y-%m-%d"
    )

# datetimes
for col in ["APPT_DTTM", "CHECKIN_DTTM", "CHECKOUT_DTTM"]:
    df[col] = pd.to_datetime(df[col], infer_datetime_format=True)

# times
for col in ["CHAIR_IN", "INFUSION_START", "INFUSION_END", "CHAIR_OUT"]:
    df[col] = pd.to_datetime(df["CHECKIN_DTTM"]).dt.strftime("%Y-%m-%d ") + df[col]
    df[col] = pd.to_datetime(df[col], infer_datetime_format=True)

# Removes rows with dates outside of range (using ~> instead of < ignores nans)
startDate = pd.to_datetime("2021-10-31 00:00:00")
endDate = pd.to_datetime("2021-11-04 23:59:59")
for col in [
    "CHECKIN_DTTM",
    "CHECKOUT_DTTM",
    "CHAIR_IN",
    "INFUSION_START",
    "INFUSION_END",
    "CHAIR_OUT",
]:
    df = df[~(df[col] > endDate)]
    df = df[~(df[col] < startDate)]

# Drops all duplicate appt rows
# This allows calculation based on appointments, not infusions
dfAppt = df.drop_duplicates("INPATIENT_DATA_ID_x")[
    [
        "INPATIENT_DATA_ID_x",
        "APPT_LENGTH",
        "APPT_STATUS_NAME",
        "APPT_DTTM",
        "CHECKIN_DTTM",
        "CHAIR_IN",
        "INFUSION_START",
        "INFUSION_END",
        "CHAIR_OUT",
        "CHECKOUT_DTTM",
        "ORDER_STATUS",
    ]
]

# Sets time values to min and max of all appointment rows
for appt in dfAppt["INPATIENT_DATA_ID_x"]:
    for colName in ["CHECKIN_DTTM", "CHAIR_IN", "INFUSION_START"]:
        dfAppt.loc[dfAppt["INPATIENT_DATA_ID_x"] == appt, colName] = (
            df.loc[df["INPATIENT_DATA_ID_x"] == appt, colName].dropna().min()
        )
    for colName in ["CHECKOUT_DTTM", "CHAIR_OUT", "INFUSION_END"]:
        dfAppt.loc[dfAppt["INPATIENT_DATA_ID_x"] == appt, colName] = (
            df.loc[df["INPATIENT_DATA_ID_x"] == appt, colName].dropna().max()
        )

# Remove any times that are impossible (occurring out of order)
df_ordered = dfAppt[~(dfAppt["CHECKIN_DTTM"] > dfAppt["CHAIR_IN"])]
df_ordered = df_ordered[~(df_ordered["CHAIR_IN"] > df_ordered["INFUSION_START"])]
df_ordered = df_ordered[~(df_ordered["INFUSION_START"] > df_ordered["INFUSION_END"])]
df_ordered = df_ordered[~(df_ordered["INFUSION_END"] > df_ordered["CHAIR_OUT"])]
df_ordered = df_ordered[~(df_ordered["CHAIR_OUT"] > df_ordered["CHECKOUT_DTTM"])]

# Create wait time column
df_ordered["WAIT_TIME"] = df_ordered["CHAIR_IN"] - df_ordered["CHECKIN_DTTM"]

# Sort by wait time and print table
print(
    df_ordered[
        [
            "INPATIENT_DATA_ID_x",
            "CHECKIN_DTTM",
            "CHAIR_IN",
            "INFUSION_END",
            "WAIT_TIME",
        ]
    ]
    .dropna()
    .sort_values("WAIT_TIME")
)

# Print final calculations
print(
    "After checking in, the average patient waits "
    + str(df_ordered["WAIT_TIME"].dropna().mean().round("S"))
    + " before entering the chair."
)
print(
    "The average patient is "
    + str(
        (df_ordered["CHECKIN_DTTM"] - df_ordered["APPT_DTTM"])
        .dropna()
        .mean()
        .round("S")
    )
    + " late to their appointment."
)
print(
    "The average appointment is "
    + str(
        (
            (df_ordered["INFUSION_END"] - df_ordered["CHAIR_IN"])
            - pd.to_timedelta(df_ordered["APPT_LENGTH"], "minutes")
        )
        .dropna()
        .mean()
        .round("S")
    )
    + " longer than scheduled."
)

# Saves final dataframe
dfAppt.to_csv("Infusion_Data_Fixed.csv")
