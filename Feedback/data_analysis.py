import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('feedback_processed.csv')
print(df.head())

# ---------------------------------------------------------
# STEP 1: Calculate the Percentages
# ---------------------------------------------------------
# We group by 'experienced' and calculate the average (mean) for all columns
# multiplied by 100 to get percentages.
aim_cols = [col for col in df.columns if 'enjoyment_' in col and col != 'enjoyment_others']
comparison = df.groupby('experienced')[aim_cols].mean() * 100

# Transpose it so it's easier to read (Rows = Aims, Cols = Experienced Status)
comparison = comparison.T
comparison.columns = ['New Volunteers (0)', 'Experienced (1)']

print("--- Percentage of Volunteers selecting each Enjoyment ---")
print(comparison.round(1)) # Round to 1 decimal place

# ---------------------------------------------------------
# STEP 2: Visualize the Difference
# ---------------------------------------------------------
# Reshape data for plotting (Seaborn likes "long" format)
df_melted = df.melt(id_vars='experienced', value_vars=aim_cols, 
                    var_name='Enjoyment', value_name='Selected')

# Filter to only keep the 'Selected = 1' rows to count them, 
# OR easier: just plot the barplot which calculates means automatically
plt.figure(figsize=(10, 6))

# 'ci=None' removes error bars for a cleaner look
sns.barplot(data=df_melted, x='Enjoyment', y='Selected', hue='experienced', ci=None, palette='viridis')

plt.title('Comparison of Enjoyments: New vs. Experienced Volunteers')
plt.ylabel('Proportion (0.0 to 1.0)')
plt.xlabel('Enjoyment Category')
plt.legend(title='Volunteer Status', labels=['New (0)', 'Experienced (1)'])
plt.ylim(0, 1.1) # Set y-axis limit slightly above 1
plt.show()