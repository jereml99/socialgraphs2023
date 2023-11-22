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
    csv_filepath = 'all_page_names.csv'  # Replace with your CSV file path
    page_names_list = load_csv_as_list(csv_filepath)
    # The page_names_list is a list of lists. If you want a flat list of page names:
    all_page_names = [item for sublist in page_names_list for item in sublist]

    print(all_page_names)
    
    # Step 1: Get all page names
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_all_page_names_from_json, os.path.join(base_directory, subcategory, json_file))
                   for subcategory in os.listdir(base_directory)
                   for json_file in os.listdir(os.path.join(base_directory, subcategory))]
        
        for future in tqdm(futures, desc="Fetching Page Names", unit="files"):
            all_page_names.append(future.result())

    # Save all page names to CSV
    with open('all_page_names.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Page Names'])
        for page_name in all_page_names:
            writer.writerow([page_name])

    # Step 2: Update JSON files with filtered outlinks and categories
    json_files = [os.path.join(base_directory, subcategory, json_file)
                  for subcategory in os.listdir(base_directory)
                  for json_file in os.listdir(os.path.join(base_directory, subcategory))]

    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda x: update_json(x, filter_outlinks, all_page_names), json_files), 
                  total=len(json_files), desc="Filtering Outlinks", unit="files"))
        list(tqdm(executor.map(lambda x: update_json(x, add_categories), json_files), 
                  total=len(json_files), desc="Adding Categories", unit="files"))

    # Run integration test
    integration_test_on_one_file(base_directory, all_page_names)

if __name__ == '__main__':
    main()
