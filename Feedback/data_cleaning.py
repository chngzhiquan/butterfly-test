import pandas as pd

df = pd.read_csv('watches_feedback.csv')
cols_to_encode = ['watches', 'aim', 'enjoyment', 'challenges','more']
dfs_to_combine = [df] 

for col in cols_to_encode:
    # 1. Create the dummies
    # sep=';' splits "Hobby;Research" into two columns. 
    # If a column has no semicolons (like Enjoyment), it still works perfectly!
    dummies = df[col].astype(str).str.get_dummies(sep=';')
    
    # 2. Rename columns to keep them organized (e.g., "aim_Hobby", "aim_Research")
    dummies = dummies.add_prefix(f'{col}_')
    
    # 3. Add to our list
    dfs_to_combine.append(dummies)

# 4. Combine everything horizontally
df_final = pd.concat(dfs_to_combine, axis=1)

# ---------------------------------------------------------
# VIEW RESULTS
# ---------------------------------------------------------
print(df_final.head())
df_final.to_csv('feedback_processed.csv', index=False)