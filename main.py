import pandas as pd

df = pd.read_csv("LeanTaaS_Infusion_Data_Analyst_Intern_Assignment.csv")

print(df.head())

# rename CHAIR_START to CHAIR_IN to match CHAIR_OUT
df = df.rename(columns={"CHAIR_START": "CHAIR_IN"})

# Convert all datetimes to %Y-%m-%d %H:%M
# Make all times datetimes using the appt date

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

# Check that all appointments follow the correct order
# checkin < chairstart < infstart < infend < chairout < checkout
# Col Indices: 8, 12, 13, 14, 15, 9
# Split by appt status
def checkOrder(df):
    return df.iloc[3, [8, 12, 13, 14, 15, 9]].is_monotonic_increasing


print(checkOrder(df))
dfGrouped = df.groupby(df["APPT_STATUS_NAME"])
print(list(dfGrouped.groups))
for group in dfGrouped.groups:
    print(group)
    print(dfGrouped.get_group(group).iloc[:, [8, 12, 13, 14, 15, 9]])

# Arrived
# Should not be any, as all appts should be completed at this point

print(df.columns.values)
df.to_csv("Infusion_Fixed.csv")
