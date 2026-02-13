import pandas as pd

# 1. Load the Excel file
# Replace 'your_file.xlsx' with the actual name of your file
input_file = 'butterfly (raw to visualisation).xlsx'
df = pd.read_excel(input_file)

# 2. Define the columns to KEEP
# Make sure these match your Excel headers exactly! 
columns_to_keep = [
    'Ref_no_clean',
    'Year', 
    'Month', 
    'Site_clean', 
    'Transect_ID_clean', 
    'Start_Time_clean',
    'Total butterflies observed',
    'Confidence.cleaned'
]

# 3. Dynamically find all columns from 'aberrant.oakblue' onwards
# df.loc[:, 'StartColumn':] selects all columns from StartColumn to the end
species_columns = df.loc[:, 'aberrant.oakblue':].columns.tolist()

# 4. Melt using those specific lists
df_long = df.melt(
    id_vars=columns_to_keep,
    value_vars=species_columns, # Explicitly tell it WHICH columns to melt
    var_name='Species',
    value_name='Count'
)

df_long = df_long[df_long['Count'] > 0]

df_long['Species'] = df_long['Species'].str.replace('.', ' ', regex=False).str.title()
print(df_long.head())

# 5. Save to a new Excel file
output_file = 'processed_data_long.xlsx'
df_long.to_excel(output_file, index=False)
