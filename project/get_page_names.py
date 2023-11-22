import os
import json
import csv
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def get_all_page_names_from_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data['title']


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

    # Save all page names to CSV
    with open('all_page_names.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Page Names'])
        for page_name in all_page_names:
            writer.writerow([page_name])

if __name__ == '__main__':
    main()
