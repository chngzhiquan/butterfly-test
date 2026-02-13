import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# 1. Load your Excel file
# Make sure the file is in the same folder as your script
df = pd.read_excel('feedback_profiles_overall.xlsx')

# 2. Aggregation: Calculate the mean for each cluster
df_means = df.groupby('Cluster_ID').mean()

# 3. Rename the Clusters
# We map the ID (0, 1, 2) to the new descriptive names
name_mapping = {
    0: "Super", 
    1: "Casual", 
    2: "Skill Seekers"
}
df_means = df_means.rename(index=name_mapping)

# 4. Define the Radar Chart Function
def plot_overlapping_radar(df_data):
    
    # --- Setup the Variables ---
    categories = list(df_data.columns)
    N = len(categories)

    # Calculate angle for each axis (divide circle by N)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1] # Close the loop

    # --- Setup the Plot ---
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Draw one axis per variable + add labels
    plt.xticks(angles[:-1], categories, color='black', size=14)

    ax.tick_params(axis='x', which='major', pad=50)
    
    # Draw y-labels (0.2, 0.4, ... 1.0)
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["20%", "40%", "60%", "80%", "100%"], color="grey", size=7)
    plt.ylim(0, 1)

    # --- Plot Each Cluster ---
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c'] # Blue, Orange, Green
    
    # We enumerate to get a counter 'i' (for the colors) 
    # and the 'label' (Super, Casual, etc. for the legend)
    for i, (label, row) in enumerate(df_data.iterrows()):
        values = row.values.flatten().tolist()
        values += values[:1] # Close the loop
        
        # Plot the line
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=label, color=colors[i])
        
        # Fill the area
        ax.fill(angles, values, alpha=0.25, color=colors[i])

    # --- Final Touches ---
    plt.legend(loc='upper right', bbox_to_anchor=(1.9, 1.1))
    plt.show()

# 5. Run the function
plot_overlapping_radar(df_means)