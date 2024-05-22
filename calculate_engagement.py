import pandas as pd

# Function to calculate Average Engagement per View
def calculate_average_engagement_per_view(view_count, like_count, comment_count):
    if view_count == 0:
        return 0
    return (like_count + comment_count) / view_count

# Load the Excel file
file_path = input("Please enter the path to the Excel file: ")
df = pd.read_excel(file_path)

# Check if necessary columns exist
required_columns = ["View Count", "Like Count", "Comment Count"]
if not all(column in df.columns for column in required_columns):
    raise ValueError(f"The Excel file must contain the following columns: {', '.join(required_columns)}")

# Sort the DataFrame by View 
df_sorted = df.sort_values(by="View Count")

# Calculate the median view count
median_view_count = df_sorted["View Count"].median()

# Filter the DataFrame to include only videos with views greater than the median
df_filtered = df_sorted[df_sorted["View Count"] > median_view_count]

# Calculate Average Engagement per View for filtered videos
df_filtered["Average Engagement per View"] = df_filtered.apply(
    lambda row: calculate_average_engagement_per_view(row["View Count"], row["Like Count"], row["Comment Count"]),
    axis=1
) 

# Save the updated DataFrame to a new Excel file
output_file_path = file_path.replace(".xlsx", "_updated.xlsx")
df_filtered.to_excel(output_file_path, index=False)

print(f"Updated file saved as {output_file_path}")