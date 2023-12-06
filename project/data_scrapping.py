import os
import json
import pywikibot

def get_subcategories_from_category(category_name):
    site = pywikibot.Site('en', 'wikipedia')
    cat = pywikibot.Category(site, category_name)
    pages = list(cat.subcategories())
    return [page.title() for page in pages]

def get_games_from_category(category_name):
    site = pywikibot.Site('en', 'wikipedia')
    cat = pywikibot.Category(site, category_name)
    pages = list(cat.articles())
    return pages

def save_to_json(page, subcategory):
    data = {
        "text": page.text,
        "categorie": subcategory,
        "title": page.title(),
        "url": page.full_url(),
    }

    directory = os.path.join('./data', subcategory.split(':')[-1])
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, page.title().replace('/', '_') + '.json')
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def main():
    # Start with the base category
    category_name = 'Category:Video games by year'
    game_categories = get_subcategories_from_category(category_name)

    # Go through each sub-category to get the game pages
    for game_category in game_categories:
        # Make sure we only look at the relevant categories (avoiding 'by decade' etc.)
        if 'video games' in game_category.lower():
            game_pages = get_games_from_category(game_category)
            for page in game_pages:
                save_to_json(page, game_category.split(':')[-1])

if __name__ == '__main__':
    main()
