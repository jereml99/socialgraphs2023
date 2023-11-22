import os
import json
import re
import csv
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def extract_outlinks(text):
    """Extract Wikipedia outlinks (wiki links) from the text."""
    links = re.findall(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', text)
    return [link.split('#')[0] for link in links]

def extract_categories(text):
    """Extract categories from the text."""
    return re.findall(r'\[\[Category:(.*?)\]\]', text)

def get_all_page_names_from_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data['title']

# Generic function to update JSON files
def update_json(filepath, update_func, *args):
    with open(filepath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    update_func(data, *args)  # Call the provided update function
    
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def update_json_with_country_of_development(data):
    # Extract countries of development based on the categories
    countries_of_development = []
    for category in data.get('categories', []):
        match = re.match(r'Video games developed in (.+)', category)
        if match:
            country = match.group(1)
            countries_of_development.append(country)
    
    # If no countries are found, set to ["other"]
    data['country of development'] = countries_of_development if countries_of_development else ["other"]
    
                  
# Specific update methods
def filter_outlinks(data, all_page_names):
    data['outpages'] = [link for link in extract_outlinks(data['text']) if link in all_page_names]

def add_categories(data):
    data['categories'] = extract_categories(data['text'])


def integration_test_on_one_file(base_directory, all_page_names):
    test_subcategory = os.listdir(base_directory)[0]
    test_file = os.listdir(os.path.join(base_directory, test_subcategory))[0]
    test_filepath = os.path.join(base_directory, test_subcategory, test_file)
    
    print("Running integration test on:", test_filepath)
    update_json(test_filepath, filter_outlinks, all_page_names)
    update_json(test_filepath, add_categories)
    print("Test complete. Please verify", test_filepath)


def load_csv_as_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        # Skip the header row if your CSV has one
        next(reader, None)
        return list(reader)




def main():
    base_directory = 'project/data'

    # Step 2: Update JSON files with filtered outlinks and categories
    json_files = [os.path.join(base_directory, subcategory, json_file)
                  for subcategory in os.listdir(base_directory)
                  for json_file in os.listdir(os.path.join(base_directory, subcategory))]

    with ThreadPoolExecutor() as executor:
        # list(tqdm(executor.map(lambda x: update_json(x, filter_outlinks, all_page_names), json_files), 
        #           total=len(json_files), desc="Filtering Outlinks", unit="files"))
        # list(tqdm(executor.map(lambda x: update_json(x, add_categories), json_files), 
        #           total=len(json_files), desc="Adding Categories", unit="files"))
        list(tqdm(executor.map(lambda x: update_json(x, update_json_with_country_of_development), json_files), 
            total=len(json_files), desc="Adding cantry of development", unit="files"))

    # # Run integration test
    # integration_test_on_one_file(base_directory, all_page_names)

if __name__ == '__main__':
    main()
