import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Tells Python: "Don't try to open a window"
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# 1. Load Data
df = pd.read_csv('final_feedback_processed.csv')

# 2. Select columns BUT exclude text
cols_to_analyze = [c for c in df.columns if ('watches_' in c or 'enjoyment_' in c or 'hope_' in c or 'challenges_' in c or 'interest_' in c)]
# This command explicitly drops anything that isn't a number
X = df[cols_to_analyze].select_dtypes(include=['number'])

# 3. Run K-Means
# You can change n_clusters to 3 or 4 depending on how many "types" you want
kmeans = KMeans(n_clusters=3, random_state=42)
df['Cluster_ID'] = kmeans.fit_predict(X)

# 4. Create the Profile Summary
# We group by the new Cluster ID and calculate the average (percentage)
profile_summary = df.groupby('Cluster_ID')[X.columns].mean()

# 5. Visualize
plt.figure(figsize=(12, 8)) # Made it a bit bigger for readability
sns.heatmap(profile_summary.T, annot=True, cmap='RdYlGn', fmt='.2f')
plt.title('Volunteer Personas: What Defines Each Group?')
plt.xlabel('Cluster ID')
plt.ylabel('Survey Question')
plt.tight_layout()
print("Saving heatmap to 'persona_heatmap.png'...")
plt.savefig('persona_heatmap.png')
# 6. Save results for Looker Studio
df.to_csv('feedback_with_profiles.csv', index=False)