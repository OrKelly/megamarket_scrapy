from datetime import datetime
import time
from bs4 import BeautifulSoup
import requests
import fake_useragent
from selenium import webdriver
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

user = fake_useragent.UserAgent().random

headers = {
    'user-agent': user,
}

options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={user}')
options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options)
driver.maximize_window()

def get_page(url):
    try:
        driver.get(url=url)
        WebDriverWait(driver, 60).until(
            ec.presence_of_element_located((By.TAG_NAME, "html")))
        with open('market-page.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_data(url, percent):
    start_time = time.time()
    i = 1
    while True:
        print(f'scrapping {i} page')
        get_page(f'{url}page-{i}/')
        with open('market-page.html', encoding='utf-8') as file:
            source = file.read()
        print(f'getted {i} page')

        soup = BeautifulSoup(source, 'lxml')
        data = []
        curdate = datetime.now()
        with open(f'data/{datetime.strftime(curdate, "%d.%m.%Y:%H")}.json', 'a', encoding='utf-8') as file:
            items = soup.find_all('div', class_='catalog-item')
            if not items:
                end_time = time.time()
                print(f'Time of execution {end_time - start_time}')
                break
            for item in items:
                title = item.find(class_='item-title').text.strip()
                try:
                    bonus_percent = item.find(class_='bonus-percent').text.strip()
                except:
                    bonus_percent = None
                try:
                    bonus_amount = item.find(class_='bonus-amount').text.strip()
                except:
                    bonus_percent = None
                try:
                    price = item.find(class_='item-price').text.strip().replace(u"\u202F", " ")
                except:
                    price = 'Цена отсутствует'
                item_url = 'https://megamarket.ru' + item.find(class_='item-image').find('a').get('href')
                if bonus_percent:
                    if bonus_percent >= percent:
                        data.append(
                            {
                                'товар': title,
                                'цена': price,
                                'процент кэшбека': bonus_percent,
                                'сумма кэшбека': bonus_amount,
                                'ссылка': item_url
                            }
                        )
                    print(f'Added {title}')
            json.dump(data, file, ensure_ascii=False, indent=4)
            print(f'Scrapped {i} page')
            i += 1


def main():
    url = 'https://megamarket.ru/catalog/kofemashiny/'
    get_data(url, 10)

if __name__ == '__main__':
    main()
