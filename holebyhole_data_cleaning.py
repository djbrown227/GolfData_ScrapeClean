#!/usr/bin/env python
# coding: utf-8

# In[78]:


import pandas as pd
import numpy as np


# In[79]:


# Replace 'your_file.xlsx' with the path to your actual Excel file
df = pd.read_excel('/Users/danielbrown/Desktop/Golf/data/tournament_golf_scores78.xlsx')
#df = pd.read_excel('/Users/danielbrown/Desktop/tournament_golf_scores10.xlsx')
#excel 62 was not converted, #72 was not converted
df


# In[80]:


# Create a new DataFrame with rows 0 and 1 from the original DataFrame
new_df = df.iloc[0:2].copy()

# Drop rows 0 and 1 from the original DataFrame
df.drop(index=[0, 1], inplace=True)

# Reset the index of the original DataFrame if desired
df.reset_index(drop=True, inplace=True)

# Display the new DataFrame
print("New DataFrame:")
print(new_df)

# Display the modified original DataFrame
#print("\nModified Original DataFrame:")
#print(df)


# In[81]:


# Transforming the df_new
# Extract event title and event date
event_title = new_df.columns[1]  # Assuming the second column always contains the event title
event_date = new_df.iloc[0, 1]  # Assuming the first row of the second column always contains the event date

# Create a new DataFrame with the desired structure
new_df = pd.DataFrame({
    'Event Title': [event_title],
    'Event Date': [event_date]
})

from datetime import datetime
import pandas as pd

# Assuming 'new_df' is your DataFrame and it has been correctly transformed previously

# Extract the start date from the "Event Date" string
start_date_str = new_df.loc[0, 'Event Date'].split('-')[0].strip()

# Assuming the event year is always the last 4 characters of the event date string
event_year = new_df.loc[0, 'Event Date'].split(' ')[-1]

# Append the year to the start date string to form a complete date string
complete_start_date_str = f"{start_date_str}, {event_year}"

print(complete_start_date_str)
# Convert the start date string into a datetime object
# Now the format matches "%B %d, %Y"
start_date = datetime.strptime(complete_start_date_str, "%B %d, %Y")

# Replace the "Event Date" column with the datetime object
new_df['Event Date'] = start_date

# Optionally, convert the "Event Date" column to pandas datetime format for better integration with pandas
new_df['Event Date'] = pd.to_datetime(new_df['Event Date'])

# Display the DataFrame to verify the transformation
print(new_df)


# In[82]:


import pandas as pd

# Assuming 'df' is your DataFrame

# Set the first row as the new header
new_header = df.iloc[0] # Grab the first row for the header
df = df[1:] # Take the data less the header row
df.columns = new_header # Set the header row as the df header

# Reset the index of the DataFrame
df.reset_index(drop=True, inplace=True)

# Display the DataFrame to verify the changes
df


# In[83]:


#Cleaning Data
#Removing "Round 4","Round 3","Round 2","Round 1"
df = df[~df['Dropdown Value'].isin(['Round 4', 'Round 3', 'Round 2', 'Round 1'])]
df


# In[84]:


#Remove all rows where person withdraws
df = df[~df['Score'].isin(['WD'])]
df


# In[85]:


# Duplicate each row in the DataFrame 18 times
df = df.loc[np.repeat(df.index, 18)]

# Optionally, reset the index to have a continuous index
df.reset_index(drop=True, inplace=True)

# Display the first few rows of the duplicated DataFrame to verify
df


# In[86]:


import pandas as pd

# Assuming 'df' is your DataFrame

# Function to remove the first, middle, and last elements from the cell
def remove_elements(cell):
    elements = cell.split(", ")  # Split the string into a list by comma
    if len(elements) > 2:  # Check if there are enough elements to remove
        middle_index = (len(elements) // 2) - 1  # Find the middle element's index
        # Remove the first, middle, and last elements
        modified_elements = elements[1:middle_index] + elements[middle_index+1:-2]
    else:
        # If not enough elements, return the original cell or handle accordingly
        modified_elements = elements
    return ", ".join(modified_elements)  # Join the elements back into a string

# Apply the function to each cell in the 'Pars' and 'Scores' columns
df['Pars'] = df['Pars'].apply(remove_elements)
df['Scores'] = df['Scores'].apply(remove_elements)

# Display the modified DataFrame
df


# In[87]:


# Calculate the total number of rows
total_rows = len(df)

# Generate a sequence from 1 to 18, repeated for the length of the DataFrame
df['Hole'] = np.arange(1, total_rows + 1) % 18

# Replace 0 with 18, since modulo operation results in 0 for multiples of 18
df['Hole'].replace(0, 18, inplace=True)

# Display the DataFrame with the new 'Hole' column
df # Show the first 36 rows to see the repeating pattern


# In[88]:


# Function to get the nth element from a comma-separated string
def get_nth_element(s, n):
    elements = s.split(", ")
    return elements[n-1] if len(elements) >= n else None

# Apply the function to each row for both 'Pars' and 'Scores'
df['Pars'] = df.apply(lambda row: get_nth_element(row['Pars'], row['Hole']), axis=1)
df['Scores'] = df.apply(lambda row: get_nth_element(row['Scores'], row['Hole']), axis=1)

df


# In[89]:


#Rename Column
df.rename(columns={'Dropdown Value': 'Round'}, inplace=True)
df


# In[90]:


import pandas as pd

# Assuming new_df is your transformed DataFrame and df is the other DataFrame

# Determine the length of df
length_of_df = len(df)

# Create duplicate rows of new_df to match the length of df
duplicated_new_df = pd.concat([new_df] * length_of_df, ignore_index=True)

# Display the resulting DataFrame
print(duplicated_new_df)


# In[91]:


# Join duplicated_new_df and df on the index
joined_df = pd.concat([duplicated_new_df, df], axis=1)

# Display the resulting DataFrame
print(joined_df)


# In[92]:


# Extract the 'Event Title' to use in the file name
event_title = duplicated_new_df.loc[0, 'Event Title']
event_date = duplicated_new_df.loc[0, 'Event Date'].strftime('%Y_%m_%d')  # Format the date

# Replace spaces with underscores and remove potential invalid characters for filenames
file_name = f"{event_title.replace(' ', '_').replace('/', '_')}_{event_date}.xlsx"

# Construct the file path
file_path = f'/Users/danielbrown/Desktop/Golf/espn_holebyhole_cleaned/{file_name}'

# Export the joined DataFrame to an Excel file
joined_df.to_excel(file_path, index=False)

print(f"DataFrame exported to {file_path}")


# In[ ]:




