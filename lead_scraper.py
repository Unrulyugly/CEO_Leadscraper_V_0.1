import requests
import json

# API details
api_endpoint = "https://api-bcbe5a.stack.tryrelevance.com/latest/studios/9303b82c-47e7-44fc-9da4-fc64acee4d28/trigger_limited"
project_id = "c092c8198059-4a3b-914f-19ba72044df3"
headers = {"Content-Type": "application/json"}

# File paths
input_file = 'NEW_CEO.txt'  # Replace with your input file path
output_file = 'output.txt'  # Output file

# Read from input file
with open(input_file, 'r') as file:
    lines = file.readlines()

# Initialize a list to hold updated lines
updated_lines = []

# Process each line
for line in lines:
    # Find the position of "@" and extract the email URL from there
    at_pos = line.find('@')
    if at_pos != -1:
        email_url = line[at_pos+1:].strip()  # Extract domain from @ to the end of the line

        # Prepare payload for the API request
        payload = {
            "params": {"role": "CEO", "email_url": email_url},
            "project": project_id
        }

        # Make the API request
        response = requests.post(api_endpoint, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            ceo_name = data.get('output', {}).get('name', 'CEO Name Not Found')
        else:
            ceo_name = "CEO Name Not Found"

        updated_lines.append(f"CEO Name: {ceo_name}\n{line}")
    else:
        updated_lines.append(line)

# Write to output file
with open(output_file, 'w') as file:
    file.writelines(updated_lines)
