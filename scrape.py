from bs4 import BeautifulSoup
import requests
import csv
from tqdm import tqdm
from random import randint
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('--start', type=int, default=0, help='start index of url list')
parser.add_argument('--end', type=int, default=0, help='end index of url list')

args = parser.parse_args()

start_index, end_index = args.start, args.end

with open('detail-brand-list.txt', 'r') as fp:
    detail_brand_list = fp.read().split('\n')
    print("length of the link list", len(detail_brand_list))

if end_index == 0:
    end_index = len(detail_brand_list) - 1

print("Scraping from {} to {}".format(start_index, end_index))


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

# perfume.csv
perfume_file = open('perfume.csv', 'w')
perfume_writer = csv.writer(perfume_file)
perfume_writer.writerow(['f_id', 'brand_name', 'brand_score', 'brand_popular', 'brand_tag', 't', 'm', 'b'])

# reviews.csv
review_file = open('reviews.csv', 'w')
review_writer = csv.writer(review_file)
review_writer.writerow(['f_id', 'brand_name', 'u_id', 'u_name', 'review'])


for url in tqdm(detail_brand_list[start_index:end_index]):
    f_id = re.search('\/(\d+)-', url).group(1)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    find_next = soup.find("div", class_="next_news")
    find_item_info = soup.find("ul", class_="item_info")
    brand_name = soup.find("ul", class_="itemMain").h1.get_text()

    score_tag = soup.find_all("span", class_="score")
    if not score_tag:
        brand_score = '0'
    else:
        brand_score = score_tag[0].get_text()

    popular_tag=soup.find_all("span", class_="people")
    if not popular_tag:
        brand_popular = '0'
    else:
        brand_popular = popular_tag[0].get_text()
    tag_tag = soup.find_all("ul", class_="item_info")[0]
    brand_tag = [a.get_text() for a in tag_tag.find_all("a", href=lambda x: x and "field=tag" in x)]

    
    t, m, b = [], [], []
    n = None
    for note in find_item_info.li.children:
        if str(note).find("前") >= 0:
            n = t
        elif str(note).find("中") >= 0:
            n = m
        elif str(note).find("后") >= 0:
            n = b
        if note.name == "a" and n is not None and note['href'].find("qiwei") >= 0:
            n.append(note.get_text())

    perfume_writer.writerow([
        f_id, brand_name, brand_score, brand_popular, brand_tag, ' '.join(t), ' '.join(m), ' '.join(b)
    ])

    item_discuss = soup.find("li", id="itemdiscuss")
    if item_discuss.ul is None:
        continue

    for tag in item_discuss.ul.children:
        author = tag.find('div', class_='author')

        u_id = author.a['href'].split('=')[-1]
        u_name = author.a.get_text()
        review = tag.find('div', class_='hfshow').get_text()
    
        review_writer.writerow([
            f_id, brand_name, u_id, u_name, review
        ])

    if not find_next:
        continue

    lastpage = find_next.find_all("a")[-1]['href'].split('=')[-1]
    for rpage in range(1, int(lastpage)):
        rrp = requests.get("{}?page={}".format(url, rpage+1), headers=headers)
        soup_rp = BeautifulSoup(rrp.text, 'html.parser')

        item_discuss = soup_rp.find("li", id="itemdiscuss")
        for tag in item_discuss.ul.children:
            author = tag.find('div', class_='author')

            u_id = author.a['href'].split('=')[-1]
            u_name = author.a.get_text()
            review = tag.find('div', class_='hfshow').get_text()
            review_writer.writerow([
                f_id, brand_name, u_id, u_name, review
            ])


perfume_file.close()
review_file.close()


