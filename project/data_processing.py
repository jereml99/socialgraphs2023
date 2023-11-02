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

def update_json_with_filtered_outlinks(filepath, all_page_names):
    with open(filepath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    data['outpages'] = [link for link in extract_outlinks(data['text']) if link in all_page_names]
    data['categories'] = extract_categories(data['text'])

    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def integration_test_on_one_file(base_directory, all_page_names):
    test_subcategory = os.listdir(base_directory)[0]
    test_file = os.listdir(os.path.join(base_directory, test_subcategory))[0]
    test_filepath = os.path.join(base_directory, test_subcategory, test_file)
    
    print("Running integration test on:", test_filepath)
    update_json_with_filtered_outlinks(test_filepath, all_page_names)
    print("Test complete. Please verify", test_filepath)

def main():
    base_directory = 'project/data'
    all_page_names = []

    # Step 1: Get all page names
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_all_page_names_from_json, os.path.join(base_directory, subcategory, json_file))
                   for subcategory in os.listdir(base_directory)
                   for json_file in os.listdir(os.path.join(base_directory, subcategory))]
        
        for future in tqdm(futures, desc="Fetching Page Names", unit="files"):
            all_page_names.append(future.result())

    with open('all_page_names.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Page Names'])
        for page_name in all_page_names:
            writer.writerow([page_name])

    # Step 2: Update JSON files with filtered outlinks
    json_files = [os.path.join(base_directory, subcategory, json_file)
                  for subcategory in os.listdir(base_directory)
                  for json_file in os.listdir(os.path.join(base_directory, subcategory))]

    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda x: update_json_with_filtered_outlinks(x, all_page_names), json_files), 
                  total=len(json_files), desc="Updating JSONs", unit="files"))

    # # Run integration test
    # integration_test_on_one_file(base_directory, all_page_names)

if __name__ == '__main__':
    main()
