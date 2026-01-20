import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg') # Prevents window popping up (good for scripts)
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------
df = pd.read_csv('final_feedback_processed.csv')

# ---------------------------------------------------------
# 2. DATA PRE-PROCESSING (Text to Numbers)
# ---------------------------------------------------------
# Map Binary Columns
binary_map = {'Yes': 1, 'No': 0}

# Map Rating Columns (Adjust keys if your exact text differs)
rating_map = {
    'Excellent': 4, 'Good': 3, 'Average': 2, 'Fair': 1, 'Could be improved': 1
}

# Apply Mappings
df['achieved_goals_num'] = df['achieved_goals'].map(binary_map).fillna(0)
df['rate_overall_experience_num'] = df['rate_overall_experience'].map(rating_map).fillna(3)
df['rate_growth_num'] = df['rate_growth'].map(rating_map).fillna(3)

# Handle Missing Values for intensity
df['no_watches'] = df['no_watches'].fillna(0)

# ---------------------------------------------------------
# 3. DEFINE COLUMN LISTS (The Strategy)
# ---------------------------------------------------------

# LIST A: Training Columns (Psychographics / Inputs ONLY)
# We strictly exclude behaviors (watches) and outcomes (ratings) from the clustering.
# This ensures clusters are based on "Personality/Motivation".
train_cols_names = [
    c for c in df.columns 
    if ('enjoyment_' in c or 'hope_' in c or 'challenges_' in c or 'interest_' in c) 
    and 'Others' not in c
]

# LIST B: Outcome Columns (The "So What?" Variables)
# We want to see how the profiles perform.
outcome_cols = ['achieved_goals_num', 'rate_overall_experience_num', 'rate_growth_num', 'no_watches']

# LIST C: Watch Columns (Specific Behaviors)
watch_cols = [c for c in df.columns if 'watches_' in c]

# LIST D: Plotting Columns (Everything combined)
plotting_cols = outcome_cols + watch_cols + train_cols_names

# ---------------------------------------------------------
# 4. PREPARE TRAINING DATA
# ---------------------------------------------------------
X_train = df[train_cols_names].select_dtypes(include=['number'])

# Scale the training data (0 to 1) so K-Means treats all feelings equally
scaler = MinMaxScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

# ---------------------------------------------------------
# 5. RUN K-MEANS CLUSTERING
# ---------------------------------------------------------
# We train ONLY on the psychographics
kmeans = KMeans(n_clusters=3, random_state=42)
df['Cluster_ID'] = kmeans.fit_predict(X_train_scaled)

print("Clustering complete. Groups assigned based on Motivation.")

# ---------------------------------------------------------
# 6. PREPARE VISUALIZATION (Scaled Color, Raw Text)
# ---------------------------------------------------------

# A. The RAW Data (For Text)
profile_summary_raw = df.groupby('Cluster_ID')[plotting_cols].mean()

# B. The SCALED Data (For Colors)
X_plot = df[plotting_cols].select_dtypes(include=['number'])
X_plot_scaled = pd.DataFrame(scaler.fit_transform(X_plot), columns=X_plot.columns)
X_plot_scaled['Cluster_ID'] = df['Cluster_ID']
profile_summary_scaled = X_plot_scaled.groupby('Cluster_ID').mean()

# C. Create the Color Data
color_data = profile_summary_scaled.T.copy()

# LOGIC CHANGE: Instead of NaN, set the outcome rows to -1
# This keeps the data "alive" so the text still prints.
for row_name in color_data.index:
    if row_name not in train_cols_names:
        color_data.loc[row_name, :] = -1.0 

# ---------------------------------------------------------
# 7. PLOT HEATMAP
# ---------------------------------------------------------
plt.figure(figsize=(16, 18))

# Create a custom palette
# We take the standard Red-Yellow-Green map
my_cmap = matplotlib.cm.get_cmap('RdYlGn').copy()
# We tell it: "If a number is BELOW the minimum (vmin), make it Grey"
my_cmap.set_under('lightgrey')

sns.heatmap(
    color_data,                   # Data with -1s for outcomes
    annot=profile_summary_raw.T,  # Raw numbers for text
    cmap=my_cmap,                 
    vmin=0, vmax=1,               # CRITICAL: This tells the map that 0 is the floor
    fmt='.2f',
    linewidths=.5,
    linecolor='white'
)

plt.title('Thesis Analysis: Psychographic Inputs (Colored) vs. Behavioral Outputs (Grey)', fontsize=16)
plt.xlabel('Psychographic Cluster ID', fontsize=12)
plt.ylabel('Feature', fontsize=12)
plt.tight_layout()

print("Saving heatmap to 'thesis_final_grey.png'...")
plt.savefig('thesis_final_grey.png')

# ---------------------------------------------------------
# 8. SAVE DATA
# ---------------------------------------------------------
df.to_csv('feedback_with_psychographic_profiles.csv', index=False)