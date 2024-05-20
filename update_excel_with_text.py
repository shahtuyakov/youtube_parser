import pandas as pd
import os
import shutil
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_text_file(text_file_path):
    with open(text_file_path, 'r', encoding='utf-8') as file:
        text_content = file.read()
    return text_content

def update_excel_with_texts(excel_file_path, text_files_folder):
    # Read the Excel file
    df = pd.read_excel(excel_file_path)

    # List all text files in the folder
    text_files = [f for f in os.listdir(text_files_folder) if f.endswith('.txt')]
    
    # Insert the content of each text file into the corresponding row in the Excel file
    for text_file in text_files:
        text_file_path = os.path.join(text_files_folder, text_file)
        text_content = read_text_file(text_file_path)
        
        # Compare the title column with the text file name (without extension)
        text_file_name = os.path.splitext(text_file)[0]
        text_file_name = text_file_name.replace('.en', '')
        match_index = df[df['Title'] == text_file_name].index
        
        if not match_index.empty:
            df.at[match_index[0], 'Text Content'] = text_content
        else:
            logging.warning(f"No matching title found for text file '{text_file}'")

    # Save the updated DataFrame back to the Excel file
    df.to_excel(excel_file_path, index=False)
    logging.info(f"Excel file '{excel_file_path}' updated successfully with text contents.")

def remove_folders(*folders):
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            logging.info(f"Folder '{folder}' removed successfully.")
        else:
            logging.warning(f"Folder '{folder}' does not exist and cannot be removed.")

def main():
    # Ask for the path of the Excel file to process
    excel_file_path = input("Enter the path of the Excel file to process: ").strip()
    if not os.path.isfile(excel_file_path):
        logging.error(f"The file '{excel_file_path}' does not exist.")
        return

    # Ask for the path of the folder containing text files
    text_files_folder = input("Enter the path of the folder containing text files: ").strip()
    if not os.path.isdir(text_files_folder):
        logging.error(f"The folder '{text_files_folder}' does not exist.")
        return

    # Update the Excel file with the text file contents
    update_excel_with_texts(excel_file_path, text_files_folder)

    # Remove the specified folders
    youtube_subs_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'youtube_subs')
    remove_folders(text_files_folder, youtube_subs_folder)

if __name__ == '__main__':
    main()