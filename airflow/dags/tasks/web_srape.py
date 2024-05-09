from bs4 import BeautifulSoup
import csv
import pandas as pd
import requests
import time
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def clear_arxiv_file():
    if os.path.exists('arxiv_data.csv'):
        with open('arxiv_data.csv', 'w') as file:
            file.close
        with open('arxiv_data.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['title','abstract','day','month','year'])

def get_all_main_links():
    request = requests.get("https://arxiv.org/", headers=headers)
    returns_list = []
    if (request.status_code == 200):
        soup = BeautifulSoup(request.content, 'html.parser')
        all_main = soup.find('div', id='content').find_all('ul')
        all_main = all_main[:-1]
        returns_list = []
        for e in all_main:
            a = e.find_all('a')
            a = [tag for tag in a if tag.text.lower() not in ['recent', 'search', 'detailed description']]
            for link in a:
                returns_list.append(link['href'])
    return returns_list

def get_data_by_link(file):
    try:
        inside_req = requests.get(file, headers=headers)
        inside_soup = BeautifulSoup(inside_req.content, 'html.parser')

        data = inside_soup.find('div', id='content-inner')
        date = data.find('div', class_="dateline").get_text().strip()[1:-1].split(" ")

        try:
            day = int(date[-3])
        except:
            day = None

        try:
            month = month_to_int(date[-2])
        except:
            month = None
        try:
            year = int(date[-1])
        except:
            year = 2024
        
        h1_tag = inside_soup.find('h1', class_='title mathjax')
        span_tag = h1_tag.find('span', class_='descriptor')
        title = h1_tag.get_text(separator='', strip=True)
        title = title.replace(span_tag.text, '')
        
        h1_tag = inside_soup.find('blockquote', class_='abstract mathjax')
        abstract = h1_tag.get_text(separator='', strip=True)
        if abstract.startswith("Abstract:"):
            abstract = abstract[len("Abstract:"):].strip()

        return title, abstract, day, month, year
    except:
        pass

def month_to_int(month_abbr):
    # Dictionary mapping month abbreviations to integers
    month_dict = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    # Convert the month abbreviation to its corresponding integer
    return month_dict.get(month_abbr, None)

def web_scrape():
    params1 = {
        'advanced': '1',
        'terms-0-field': 'title',
        'date-filter_by': 'date_range',
        'date-from_date': '2024-01-01',
        'date-to_date': '2024-01-31',
        'size': '25',
    }
    params2 = {
        'advanced': '1',
        'terms-0-field': 'title',
        'date-filter_by': 'date_range',
        'date-from_date': '2024-02-01',
        'date-to_date': '2024-02-29',
        'size': '25',
    }
    params3 = {
        'advanced': '1',
        'terms-0-field': 'title',
        'date-filter_by': 'date_range',
        'date-from_date': '2024-03-01',
        'date-to_date': '2024-03-31',
        'size': '25',
    }
    params4 = {
        'advanced': '1',
        'terms-0-field': 'title',
        'date-filter_by': 'date_range',
        'date-from_date': '2024-04-01',
        'date-to_date': '2024-04-30',
        'size': '25',
    }
    params5 = {
        'advanced': '1',
        'terms-0-field': 'title',
        'date-filter_by': 'date_range',
        'date-from_date': '2024-05-01',
        'date-to_date': '2024-05-31',
        'size': '25',
    }

    link_from_month = [params1, params2, params3, params4, params5]

    links = get_all_main_links()
    time.sleep(1)
    clear_arxiv_file()
    df = pd.DataFrame(columns=['title','abstract','day','month','year'])
    # for link in links:
    #     if(link[1:].split('/')[0] == 'archive'):
    #         continue
    #     request = requests.get("https://arxiv.org" + link, headers=headers)
    #     soup = BeautifulSoup(request.content, 'html.parser')
    #     inside_files = [x['href'] for x in soup.find('div', id='dlpage').find_all('a', title='Abstract')]
    #     for inside_file in inside_files:
    #         title, abstract, day, month, year = get_data_by_link("https://arxiv.org" + inside_file)
    #         df = pd.concat([df, pd.DataFrame({'title' : [title], 'abstract' : [abstract], 'day': [day], 'month': [month], 'year': [year]})])
    #         time.sleep(1)
            
    for param in link_from_month:
        request = requests.get("https://arxiv.org/search/advanced", headers=headers, params= param)
        soup = BeautifulSoup(request.content, 'html.parser')
        inside_files = [x.find('a')['href'] for x in soup.find('div', class_='content').find_all('li', class_='arxiv-result')]
        for inside_file in inside_files:
            title, abstract, day, month, year = get_data_by_link(inside_file)
            df = pd.concat([df, pd.DataFrame({'title' : [title], 'abstract' : [abstract], 'day': [day], 'month': [month], 'year': [year]})])
            time.sleep(1)
    df.to_csv('/opt/airflow/data/arxiv.csv')