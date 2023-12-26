import csv
import json
import re
from typing import List

from bs4 import BeautifulSoup
import requests


def get_page(url: str) -> bytes | None:
    """
    The get_page function takes a url as an argument and returns the content of that page.
    If the request is not successful, it will return None.

    :param url: str: Specify the type of parameter that is expected to be passed into the function
    :return: The content of a webpage
    :doc-author: Trelent
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None


def parse_page(html: str) -> List[dict]:
    """
    The parse_page function takes in a BeautifulSoup object and returns a list of dictionaries.
    Each dictionary contains the name, description, and price of one computer.

    :param html: Pass the html code of a page to the function
    :return: A list of dictionaries
    :doc-author: Trelent
    """
    soup = BeautifulSoup(html, 'html.parser')

    computers_data = []
    computer_blocks = soup.find_all('div', class_='card-body')

    for block in computer_blocks:
        computer = {}

        computer['Name'] = block.find('a', class_='title')['title']
        computer['Description'] = block.find('p', class_='description card-text').text.strip()
        computer['Price'] = block.find('h4', class_='price').text.strip()

        computers_data.append(computer)

    return computers_data


def get_pagination_links(html: str, url: str) -> List[str]:
    """
    The get_pagination_links function takes in a url and returns a list of urls that are the pagination links.
        Args:
            html (str): The HTML content of the page to be parsed.
            url (str): The URL for which we want to get pagination links.

    :param html: Pass the html code of a page to the function
    :param url: str: Pass the url of the page to be scraped
    :return: A list of links to the pages with
    :doc-author: Trelent
    """
    soup = BeautifulSoup(html, 'html.parser')
    page_links = [url]

    pattern = r'(https?://[\w.-]+)/.*'
    matches = re.match(pattern, url)

    pagination = soup.find('ul', class_='pagination')

    if pagination:
        page_links_href = pagination.find_all('a', class_='page-link')

        for link in page_links_href:
            link_atr = link['href']
            page_link = matches.group(1) + link_atr
            page_links.append(page_link)
        return page_links
    else:
        return []


def save_to_csv(data: List[List[dict]], filename: str) -> None:
    """
    The save_to_csv function takes a list of lists of dictionaries and saves it to a csv file.

    :param data: List[List[dict]]: Pass the data to be written into the csv file
    :param filename: str: Specify the name of the file that will be saved
    :return: None
    :doc-author: Trelent
    """
    if data:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0][0].keys() if data[0] else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for rows in data:
                for row in rows:
                    writer.writerow(row)


def save_to_json(data: List[List[dict]], filename: str) -> None:
    """
    The save_to_json function takes a list of dictionaries and saves it to a json file.
        Args:
            data (List[dict]): A list of dictionaries containing the scraped data.
            filename (str): The name of the json file to be saved.

    :param data: List[List[dict]]: Pass the data to be saved
    :param filename: str: Tell the function what file to save the data to
    :return: None
    :doc-author: Trelent
    """
    if data:
        flat_data = [item for sublist in data for item in sublist]
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(flat_data, jsonfile, ensure_ascii=False, indent=4)

if __name__ == '__main__':

    base_url = 'https://webscraper.io/test-sites/e-commerce/static/computers/laptops'
    all_data = []
    html = get_page(base_url)

    pagination_links = get_pagination_links(html, base_url)

    #print(pagination_links)

    if pagination_links:

        for page in pagination_links:
            html = get_page(page)
            page_data = parse_page(html)
            all_data.append(page_data)

        print(all_data)

        if all_data:
            csv_filename = 'computers_data.csv'
            json_filename = 'computers_data.json'
            save_to_csv(all_data, csv_filename)
            save_to_json(all_data, json_filename)

            print(f'All data had been saved into {csv_filename} and {json_filename}')
        else:
            print("Couldn't save data into the files")
    else:
        print(f"Couldn't get the page")
