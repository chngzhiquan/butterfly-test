import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# 1. Load Data
df = pd.read_csv('final_feedback_processed.csv')

# --- STEP A: PREPARE YOUR EXISTING COLUMNS ---
# Select the columns you were already using (watches, enjoyment, etc.)
# We filter for columns that are already 0/1 or numbers
cols_to_analyze = [c for c in df.columns if ('watches_' in c or 'enjoyment_' in c or 'hope_' in c or 'challenges_' in c or 'interest_' in c)]
df_binary = df[cols_to_analyze].select_dtypes(include=['number']).astype(bool)

# --- STEP B: PREPARE THE NEW VARIABLES (THE FIX) ---

# 1. Handle "achieved_goals" (Converting "Yes"/"No" to True/False)
# We use .map() because .astype(bool) would incorrectly make "No" equal to True.
# If there are blank values, we fill them with False first.
df_target = df[['achieved_goals']].fillna('No').copy()
df_target['achieved_goals'] = df_target['achieved_goals'].map({'Yes': True, 'No': False})

# 2. Handle the Ordinal Ratings (rate_overall_experience, rate_growth)
# We turn "5" into a column named "Exp_5", "4" into "Exp_4", etc.
cols_ordinal = ['rate_overall_experience', 'rate_growth']
# Ensure they are strings first so get_dummies treats them as categories
df_ordinal = pd.get_dummies(df[cols_ordinal].astype(str), prefix=['Exp', 'Growth']).astype(bool)

# --- STEP C: MERGE EVERYTHING ---
# Combine all three parts into one big table
df_final = pd.concat([df_binary, df_target, df_ordinal], axis=1)

# Debug: Print columns to check
print(f"Total Columns for Analysis: {len(df_final.columns)}")
# Check specifically if achieved_goals looks right (should be True/False now)
print("Check target column:", df_final['achieved_goals'].unique())

# 3. Run Apriori
# min_support=0.05 is safe. If it's too slow, raise it to 0.1
frequent_itemsets = apriori(df_final, min_support=0.2, use_colnames=True)

# 4. Generate Rules
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.1)

# 5. Clean up output
top_rules = rules.copy()
top_rules['antecedents'] = top_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
top_rules['consequents'] = top_rules['consequents'].apply(lambda x: ', '.join(list(x)))

# 6. Filter and Sort
# We filter for strong lift (>1.1) and decent confidence (>0.5)
final_view = top_rules[
    (top_rules['lift'] > 1.1) & 
    (top_rules['confidence'] > 0.5)
].sort_values(['lift', 'confidence'], ascending=[False, False])

# 7. View and Save
print(final_view[['antecedents', 'consequents', 'confidence', 'lift']].head(15))
final_view.to_csv('association_rules_results_extended.csv', index=False)