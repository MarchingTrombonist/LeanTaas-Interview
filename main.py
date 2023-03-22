import pandas as pd
import numpy as np

df = pd.read_csv("LeanTaaS_Infusion_Data_Analyst_Intern_Assignment.csv")

# print(df.head())

# rename CHAIR_START to CHAIR_IN to match CHAIR_OUT
df = df.rename(columns={"CHAIR_START": "CHAIR_IN"})


# Add Notes column; move notes from descriptions
dfSplit = df["ORDER_DESCRIPTION"].str.split("\n", n=1, expand=True)
df["ORDER_DESCRIPTION"] = dfSplit[0]
df.insert(17, "ORDER_NOTES", dfSplit[1])


# Convert all datetimes to %Y-%m-%d %H:%M
# Make all times datetimes using the appt date

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


# Removes rows with dates outside of range
for col in [
    "APPT_DTTM",
    "CHECKIN_DTTM",
    "CHECKOUT_DTTM",
    "CHAIR_IN",
    "INFUSION_START",
    "INFUSION_END",
    "CHAIR_OUT",
]:
    df = df[~(df[col] > "2021-11-04")]
    df = df[~(df[col] < "2021-10-31")]


# Fix 11/4 extra column (column 20)
badRows = df[~df.iloc[:, 20].isna()].index
for colNum in range(18, 20):
    df.iloc[badRows, colNum] = df.iloc[badRows, colNum + 1]

df = df.iloc[:, ~df.columns.str.match("Unnamed")]


# DEPRECATED~~~~~~~~~~~~~~~~~~~~~~
# Check that all appointments follow the correct order
# CHECKIN_DTTM < CHAIR_IN < INFUSION_START < INFUSION_END < CHAIR_OUT < CHECKOUT_DTTM
# Col Indices: 8, 12, 13, 14, 15, 9
# ["CHECKIN_DTTM","CHAIR_IN","INFUSION_START","INFUSION_END","CHECKOUT_DTTM"]
# Returns all rows where all times exist and are in an increasing order
# Both removes rows with nans and rows where times are out of order
# Can probably be optimized, but I couldn't figure out a way to use pandas parsing
# .is_monotonic_increasing is an attribute, not a function, so apply() doesn't work

# df_ordered = df.iloc[
#     [
#         row
#         for row in df.index
#         if (df.iloc[row, [8, 12, 13, 14, 9]].is_monotonic_increasing)
#     ],
#     :,
# ]

# Split by appt status

# # Arrived: 1 appt
# print(
#     df_ordered[df_ordered["APPT_STATUS_NAME"] == "Arrived"].iloc[
#         :, [5, 8, 12, 13, 14, 9]
#     ]
# )
# # Cancelled: 0 appt
# print(
#     df_ordered[df_ordered["APPT_STATUS_NAME"] == "Cancelled"].iloc[
#         :, [5, 8, 12, 13, 14, 9]
#     ]
# )
# # Completed: 140 appt
# print(
#     df_ordered[df_ordered["APPT_STATUS_NAME"] == "Completed"].iloc[
#         :, [5, 8, 12, 13, 14, 9]
#     ]
# )
# # Scheduled: 0 appt
# print(
#     df_ordered[df_ordered["APPT_STATUS_NAME"] == "Scheduled"].iloc[
#         :, [5, 8, 12, 13, 14, 9]
#     ]
# )
# DEPRECATED~~~~~~~~~~~~~~~~~~~~~~

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

for appt in dfAppt["INPATIENT_DATA_ID_x"]:
    for colName in ["CHECKIN_DTTM", "CHAIR_IN", "INFUSION_START"]:
        dfAppt.loc[dfAppt["INPATIENT_DATA_ID_x"] == appt, colName] = (
            df.loc[df["INPATIENT_DATA_ID_x"] == appt, colName].dropna().min()
        )
    for colName in ["CHECKOUT_DTTM", "CHAIR_OUT", "INFUSION_END"]:
        dfAppt.loc[dfAppt["INPATIENT_DATA_ID_x"] == appt, colName] = (
            df.loc[df["INPATIENT_DATA_ID_x"] == appt, colName].dropna().max()
        )

        # print(
        #     dfAppt[
        # [
        #     "INPATIENT_DATA_ID_x",
        #     "CHECKIN_DTTM",
        #     "CHAIR_IN",
        #     "INFUSION_START",
        #     "INFUSION_END",
        #     "CHECKOUT_DTTM",
        # ]
#     ]
# )

# Remove any with infusions that end before they've checked in
df_ordered = dfAppt[dfAppt["CHECKIN_DTTM"] < dfAppt["INFUSION_END"]]

df_ordered["APPT_DELTA"] = df_ordered["INFUSION_END"] - df_ordered["CHECKIN_DTTM"]
print(
    df_ordered[["INPATIENT_DATA_ID_x", "INFUSION_END", "CHECKIN_DTTM", "APPT_DELTA"]]
    .dropna()
    .sort_values("APPT_DELTA")
)
print(df_ordered["APPT_DELTA"].dropna().mean())
