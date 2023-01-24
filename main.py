import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import psycopg2
from datetime import datetime, date, timedelta
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}


def scrape_page(url):
    rec = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(rec.text, 'lxml')
    get_data(soup)
    next_page_link = soup.find('a', attrs={'title': 'Next'})
    if next_page_link is not None:
        item_href = "https://www.kijiji.ca" + next_page_link.get('href')
        scrape_page(url=item_href)
    else:
        print('Done')


def get_data(soup):
    try:
        connection = psycopg2.connect(dbname='scraping',
                                      user='postgres',
                                      password='orozbekov',
                                      host='localhost',
                                      port="5432")

        content_container = soup.find('div', class_='container-results large-images').find_next()
        all_content = content_container.find_all('div', class_='clearfix')
        for item in all_content:
            item_img = item.find('div', class_='image').find('img').get('data-src')
            if item_img is None:
                item_img = 'no image'
            item_price = item.find('div', class_='price').text.strip()
            if item_price == 'Please Contact' or item_price == 'Free':
                item_currency = '$'
                item_price = float()
            else:
                item_currency = item_price[0]
                if len(item_price) > 9:
                    item_price = item_price[:9]
                item_price = float(item_price[1:-1].replace(',', ''))

            item_data = item.find('span', class_='date-posted').text
            if item_data[0] == '<':
                item_data = date.today()
            elif item_data == 'Yesterday':
                item_data = date.today() - timedelta(days=1)
            else:
                item_data = datetime.strptime(item_data, '%d/%m/%Y').date()
            cursor = connection.cursor()
            insert = """INSERT INTO module1 (url, price, currency, date) VALUES (%s, %s, %s, %s)"""
            insert_values = (item_img, item_price, item_currency, item_data)
            cursor.execute(insert, insert_values)
            connection.commit()
            print('1 элемент успешно добавлен')
    except psycopg2.Error as e:
        print("Ошибка при работе с PostgreSQL", e)
    finally:
        if connection:
            cursor.close()
            connection.close()


def main():
    scrape_page(url='https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273')
    sleep(randint(2, 6))


if __name__ == '__main__':
    main()
