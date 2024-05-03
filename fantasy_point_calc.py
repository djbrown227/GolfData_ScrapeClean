#!/usr/bin/env python
# coding: utf-8

# In[79]:


import os
import pandas as pd

# Define the folder path
folder_path = "/Users/danielbrown/Desktop/Golf_Raw_Data"

# Define the output file name
output_file = "/Users/danielbrown/Desktop/Golf_Raw_Data/merged_output.csv"

def merge_files(folder_path, output_file):
    # Initialize an empty list to store DataFrames
    dfs = []
    
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path):
            try:
                # Read each file as a DataFrame and append it to the list
                df = pd.read_excel(file_path, engine='openpyxl')  # Specify the engine as 'openpyxl'
                dfs.append(df)
            except Exception as e:
                print(f"Skipping file '{filename}' due to error: {e}")
    
    if not dfs:
        print("No valid Excel files found in the folder.")
        return None
    
    # Concatenate all DataFrames in the list along rows
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Print the merged DataFrame
    print("Merged DataFrame:")
    print(merged_df)
    
    # Save the merged DataFrame to a CSV file
    merged_df.to_csv(output_file, index=False)
    print(f"Merged DataFrame saved to {output_file}")
    
    return merged_df  # Return the merged DataFrame

# Call the function to merge files
merged_df = merge_files(folder_path, output_file)

# Now you can use the merged_df DataFrame outside the function
print("DataFrame Name:", type(merged_df))

df = merged_df

df.to_csv(r"/Users/danielbrown/Desktop/Golfer_event_hole.csv")


# In[80]:


# Display basic info about the DataFrame
print("DataFrame Info:")
print(df.info())

# Count NaN values for each column
print("\nCount of NaN Values:")
print(df.isna().sum())

# Convert non-numeric values in 'Score' and 'Scores' columns to NaN
#df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
df['Scores'] = pd.to_numeric(df['Scores'], errors='coerce')

# Calculate summary statistics for numeric columns
print("\nSummary Statistics:")
print(df.describe())


# In[81]:


df = df.dropna()

# Display basic info about the DataFrame
print("DataFrame Info:")
print(df.info())

# Count NaN values for each column
print("\nCount of NaN Values:")
print(df.isna().sum())

# Calculate summary statistics for numeric columns
print("\nSummary Statistics:")
print(df.describe())


# In[82]:


# Assuming df is your DataFrame
df = df[df['Event Title'] != 'Barracuda Championship']

# Display the filtered DataFrame
print(df)


# In[83]:


# Convert 'Pars' and 'Scores' columns to numeric
df['Pars'] = pd.to_numeric(df['Pars'], errors='coerce')
df['Scores'] = pd.to_numeric(df['Scores'], errors='coerce')

# Define the function to check each score type
def check_score_type(row, score_name, condition):
    if condition(row):
        return 1
    else:
        return 0

# Define conditions for each score type
conditions = {
    'Double_Eagle_or_Better': lambda row: row['Pars'] - row['Scores'] >= 3,
    'Eagle': lambda row: row['Pars'] - row['Scores'] == 2,
    'Birdie': lambda row: row['Pars'] - row['Scores'] == 1,
    'Par': lambda row: row['Pars'] - row['Scores'] == 0,
    'Bogey': lambda row: row['Pars'] - row['Scores'] == -1,
    'Double_Bogey': lambda row: row['Pars'] - row['Scores'] == -2,
    'Worse_than_Double_Bogey': lambda row: row['Pars'] - row['Scores'] < -2,
}

# Create columns for each score type
for score_name, condition in conditions.items():
    df[score_name] = df.apply(check_score_type, axis=1, args=(score_name, condition))

df


# In[84]:


df_scores = df[['Event Title', 'Event Date', 'Player Name', 'Score']]


# In[85]:


# Display basic info about the DataFrame
print("DataFrame Info:")
print(df.info())

# Count NaN values for each column
print("\nCount of NaN Values:")
print(df.isna().sum())

# Convert non-numeric values in 'Score' and 'Scores' columns to NaN
#df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
df['Scores'] = pd.to_numeric(df['Scores'], errors='coerce')

# Calculate summary statistics for numeric columns
print("\nSummary Statistics:")
print(df.describe())


# In[86]:


# Define the condition for a hole in one
def check_hole_in_one(row):
    return 1 if row['Scores'] == 1 else 0

# Create the 'Hole_in_1' column
df['Hole_in_1'] = df.apply(check_hole_in_one, axis=1)


# In[87]:


# Assuming df is your DataFrame
# Ensure the data is sorted properly
df = df.sort_values(by=['Event Title', 'Event Date', 'Player Name', 'Round', 'Hole'])

# Calculate the score relative to par for each hole
df['Score_Relative_to_Par'] = df['Scores'] - df['Pars']

# Group by player and tournament to calculate the cumulative score
df['Cumulative_Score'] = df.groupby(['Event Title', 'Event Date', 'Player Name'])['Scores'].cumsum()

# Display the DataFrame
#print(df[['Event Title', 'Event Date', 'Player Name', 'Round', 'Hole', 'Scores', 'Pars', 'Score_Relative_to_Par', 'Cumulative_Score']])


# In[88]:


#df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[89]:


# Identify birdies or better
df['Birdie_or_Better'] = df['Birdie'] | df['Eagle'] | df['Double_Eagle_or_Better']

# Initialize the streak column with 0
df['Streak_of_3_Birdies_or_Better'] = 0

# Function to check streaks and mark only the first occurrence in each round for each player
def mark_first_streak(group):
    # Find indices where a streak of 3 is completed
    streak_indices = group['Birdie_or_Better'].rolling(window=3, min_periods=3).sum() == 3
    streak_indices = streak_indices[streak_indices].index

    if not streak_indices.empty:
        # Mark only the first occurrence of the streak completion
        group.at[streak_indices[0], 'Streak_of_3_Birdies_or_Better'] = 1
    
    return group

# Apply the function to each group
df = df.groupby(['Event Title', 'Event Date', 'Player Name', 'Round']).apply(mark_first_streak)

# Drop the temporary column
df = df.drop('Birdie_or_Better', axis=1)

# Now df has the 'Streak_of_3_Birdies_or_Better' column with 1 indicating the row where the third consecutive birdie or better was hit
#print(df[['Event Title', 'Player Name', 'Round', 'Hole', 'Streak_of_3_Birdies_or_Better']])
#df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[90]:


# Step 1: Identify Par or Better
df['Par_or_Better'] = df['Par'] | df['Birdie'] | df['Eagle'] | df['Double_Eagle_or_Better']

# Initialize the Bogey Free Round column with 0
df['Bogey_Free_Round'] = 0

# Step 2 & 3: Determine Bogey Free Rounds
def mark_bogey_free_round(group):
    if group['Par_or_Better'].all():  # Check if all holes are par or better
        # Mark the last hole of the round
        group.at[group.index[-1], 'Bogey_Free_Round'] = 1
    return group

# Apply the function to each group
df = df.groupby(['Event Title', 'Event Date', 'Player Name', 'Round']).apply(mark_bogey_free_round)

# Drop the temporary column
df = df.drop('Par_or_Better', axis=1)

# Now df has the 'Bogey_Free_Round' column with 1 indicating the last hole of a bogey-free round
#print(df[['Event Title', 'Player Name', 'Round', 'Hole', 'Bogey_Free_Round']])
#df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[91]:


# Sort the dataframe to ensure the order is correct
df.sort_values(by=['Event Title', 'Event Date', 'Player Name', 'Round', 'Hole'], inplace=True)

# Calculate the cumulative score for each player for each round
df['Cumulative_Score'] = df.groupby(['Event Title', 'Event Date', 'Player Name', 'Round'])['Scores'].cumsum()

# Print the first few rows of the dataframe to verify
#print(df.head())
#df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[92]:


# Initialize the binary column with default value of 0
df['Under_70_All_Rounds'] = 0

# Define a function to calculate if under 70 strokes for all rounds
def under_70_all_rounds(group):
    # Check if all rounds are under 70 strokes at the 18th hole
    if all(group.loc[group['Hole'] == 18, 'Cumulative_Score'] < 70):
        # Find the index of the last hole of the 4th round
        last_hole_4th_round_idx = group.loc[(group['Round'] == 4) & (group['Hole'] == 18)].index
        # Set the value to 1 at the last hole of the 4th round
        group.loc[last_hole_4th_round_idx, 'Under_70_All_Rounds'] = 1
    return group

# Apply the function to each group of player within each tournament and date
df = df.groupby(['Event Title', 'Event Date', 'Player Name'], group_keys=False).apply(under_70_all_rounds)

# Now, df has a binary column 'Under_70_All_Rounds' that marks 1 for players scoring under 70 strokes
# by the end of all rounds, only on the last hole of the 4th round.
print(df[['Event Title', 'Player Name', 'Round', 'Hole', 'Cumulative_Score', 'Under_70_All_Rounds']])
df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[93]:


# Calculate cumulative score disregarding rounds, just cumulatively summing over all holes played
df['Overall_Cumulative_Score'] = df.groupby(['Event Title', 'Event Date', 'Player Name'])['Scores'].cumsum()

# Now df has a column 'Overall_Cumulative_Score' that tracks the cumulative score for each player over all rounds played.
print(df[['Event Title', 'Player Name', 'Round', 'Hole', 'Scores', 'Overall_Cumulative_Score']])
df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[94]:


# Sort the dataframe to ensure the ranking is done in the playing sequence
df = df.sort_values(by=['Event Title', 'Event Date', 'Round', 'Hole'])

# Calculate the running position of golfers for each hole
df['Position_At_Hole'] = df.groupby(['Event Title', 'Event Date', 'Round', 'Hole'])['Overall_Cumulative_Score']                           .rank(method='min', ascending=True).astype(int)

# Display the dataframe with the new 'Position_At_Hole' column
#print(df[['Event Title', 'Player Name', 'Round', 'Hole', 'Scores', 'Overall_Cumulative_Score', 'Position_At_Hole']])

# Reorder the dataframe according to Event title, Name, Round then hole
df = df.sort_values(by=['Event Title', 'Player Name', 'Round', 'Hole'])

df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[95]:


# Calculate the cumulative score relative to par for each player
df['Cumulative_Score_Relative_to_Par'] = df.groupby(['Event Title', 'Event Date', 'Player Name'])['Score_Relative_to_Par'].cumsum()

# Display the dataframe with the new 'Cumulative_Score_Relative_to_Par' column
print(df[['Event Title', 'Player Name', 'Round', 'Hole', 'Score_Relative_to_Par', 'Cumulative_Score_Relative_to_Par']])
df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[96]:


#Fantasy Points besides the ranking Points
df['FPTS'] = 13*df['Double_Eagle_or_Better'] + 8*df['Eagle'] + 3*df["Birdie"] + 0.5*df['Par'] + (-0.5)*df['Bogey'] + (-1)*df['Double_Bogey'] + (-1)*df['Worse_than_Double_Bogey'] + 5*df['Hole_in_1'] + 3*df['Streak_of_3_Birdies_or_Better'] + 3*df['Bogey_Free_Round'] + 5*df['Under_70_All_Rounds']
df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[97]:


# Calculate the cumulative sum of FPTS for each player in the tournament over all rounds.
df['Cumulative_FPTS'] = df.groupby(['Event Title', 'Player Name', 'Event Date'])['FPTS'].cumsum()

# Now, df has a 'Cumulative_FPTS' column with the cumulative fantasy points for each player.
df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[98]:


import pandas as pd

# Assuming df is your DataFrame
# Sort the DataFrame by cumulative points column in descending order
df_sorted = df.sort_values(by='Cumulative_FPTS', ascending=False)

# Display the sorted DataFrame
print(df_sorted)


# In[99]:


# Describe the sorted DataFrame
description = df_sorted.describe()

# Display the summary statistics
print(description)


# In[100]:


# Define the mapping from position to points based on tournament finish scoring
def map_position_to_points(position):
    if position == 1:
        return 30
    elif position == 2:
        return 20
    elif position == 3:
        return 18
    elif position == 4:
        return 16
    elif position == 5:
        return 14
    elif position == 6:
        return 12
    elif position == 7:
        return 10
    elif position == 8:
        return 9
    elif position == 9:
        return 8
    elif position == 10:
        return 7
    elif 11 <= position <= 15:
        return 6
    elif 16 <= position <= 20:
        return 5
    elif 21 <= position <= 25:
        return 4
    elif 26 <= position <= 30:
        return 3
    elif 31 <= position <= 40:
        return 2
    elif 41 <= position <= 50:
        return 1
    else:
        return 0

# Assuming 'df' is your dataframe and 'Position_At_Hole' has been calculated.
# Apply the mapping function to the 'Position_At_Hole' column
df['FPTS_Positions'] = df['Position_At_Hole'].apply(map_position_to_points)

# Now you can view or save your dataframe with the new column added
# print(df[['Player Name', 'Round', 'Hole', 'Position_At_Hole', 'FPTS_Positions']])
#df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe.csv")


# In[101]:


df['Total_FPTS'] = df['FPTS_Positions'] + df['Cumulative_FPTS']
df.to_csv(r"/Users/danielbrown/Desktop/Golfer_Dataframe_total.csv")
print(df)


# In[102]:


# Filter out rows with "/" in the column Player Name
df = df[~df['Player Name'].str.contains('/')]

# Display the resulting dataframe
print(df)


# In[ ]:





# In[103]:


# Display basic info about the DataFrame
print("DataFrame Info:")
print(df.info())

# Count NaN values for each column
print("\nCount of NaN Values:")
print(df.isna().sum())

# Calculate summary statistics for numeric columns
print("\nSummary Statistics:")
print(df.describe())


# In[104]:


# Count the occurrences of "CUT" in the "Score" column
cut_count = (df['Score'] == 'CUT').sum()

# Display the count
print("Count of 'CUT' scores:", cut_count)


# In[ ]:




