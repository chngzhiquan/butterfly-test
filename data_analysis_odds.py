import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# 1. Load Data
df = pd.read_csv('final_feedback_processed.csv')

# 2. Select columns BUT exclude text
# We filter for columns that contain your keywords AND are numeric (numbers)
cols_to_analyze = [c for c in df.columns if ('watches_' in c or 'enjoyment_' in c or 'hope_' in c or 'challenges_' in c or 'interest_' in c)]
df_dummies = df[cols_to_analyze].select_dtypes(include=['number']).astype(bool)

print(df_dummies.head())

# --- SAFETY CHECK ---
# This prints the columns we are using just to be sure no text sneaked in
print("Analyzing these columns:", df_dummies.columns.tolist())

# 3. Run Apriori (Find patterns in >5% of rows)
frequent_itemsets = apriori(df_dummies, min_support=0.1, use_colnames=True)

# 4. Generate Rules
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.1)
top_rules = rules[rules['confidence'] > 0.6].sort_values('lift', ascending=False)

# 5. Clean up output
top_rules['antecedents'] = top_rules['antecedents'].apply(lambda x: list(x)[0])
top_rules['consequents'] = top_rules['consequents'].apply(lambda x: list(x)[0])

print(top_rules[['antecedents', 'consequents', 'confidence', 'lift']].head(10))
top_rules.to_csv('association_rules_results.csv', index=False)