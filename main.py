import pandas as pd

df = pd.read_csv("LeanTaaS_Infusion_Data_Analyst_Intern_Assignment.csv")

# print(df.head())

# rename CHAIR_START to CHAIR_IN to match CHAIR_OUT
df = df.rename(columns={"CHAIR_START": "CHAIR_IN"})

# Convert all datetimes to %Y-%m-%d %H:%M
# Make all times datetimes using the appt date

# dates
for col in ["CONTACT_DATE", "APPT_MADE_DATE", "APPT_CANC_DATE"]:
    df[col] = pd.to_datetime(df[col], infer_datetime_format=True).dt.strftime(
        "%Y-%m-%d"
    )

# datetimes
for col in ["APPT_DTTM", "CHECKIN_DTTM", "CHECKOUT_DTTM"]:
    df[col] = pd.to_datetime(df[col], infer_datetime_format=True).dt.strftime(
        "%Y-%m-%d %H:%M"
    )

# times
for col in ["CHAIR_IN", "INFUSION_START", "INFUSION_END", "CHAIR_OUT"]:
    df[col] = pd.to_datetime(df["APPT_DTTM"]).dt.strftime("%Y-%m-%d ") + df[col]
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

# Check that all appointments follow the correct order
# CHECKIN_DTTM < CHAIR_IN < INFUSION_START < INFUSION_END < CHAIR_OUT < CHECKOUT_DTTM
# Col Indices: 8, 12, 13, 14, 15, 9
# ["CHECKIN_DTTM","CHAIR_IN","INFUSION_START","INFUSION_END","CHECKOUT_DTTM"]
# Split by appt status

# Returns all rows where all times exist and are in an increasing order
# Both removes rows with nans and rows where times are out of order
# Can probably be optimized, but I couldn't figure out a way to use pandas parsing
# .is_monotonic_increasing is an attribute, not a function, so apply() doesn't work
df_ordered = df.iloc[
    [
        row
        for row in df.index
        if (df.iloc[row, [8, 12, 13, 14, 9]].is_monotonic_increasing)
    ],
    :,
]

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

# print(df.columns.values)
# df.to_csv("Infusion_Fixed.csv")

dfGrouped = df
for col in [
    "CHECKIN_DTTM",
    "CHAIR_IN",
    "INFUSION_START",
    "INFUSION_END",
    "CHECKOUT_DTTM",
]:
    dfGrouped[col] = dfGrouped.groupby("INPATIENT_DATA_ID_x")[col].max()

print(
    dfGrouped[
        [
            "INPATIENT_DATA_ID_x",
            "CHECKIN_DTTM",
            "CHAIR_IN",
            "INFUSION_START",
            "INFUSION_END",
            "CHECKOUT_DTTM",
        ]
    ]
)
