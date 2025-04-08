import urllib.request
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from concurrent.futures import ThreadPoolExecutor

from time import sleep

SITE = r'https://www.goodreads.com'
GENRES = ['art', 'biography', 'business', 'childrens', 'comics', 'cookbooks', 'crime', 'fantasy', 'fiction', 'history', 'horror', 'psychology', 'romance', 'science', 'science-fiction', 'philosophy']


def getting_isbn(title):
    search_url = r"https://isbnsearch.org/"
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(search_url)

    driver.find_element(By.XPATH, '//*[@id="searchQuery"]').send_keys(title)
    driver.find_element(By.XPATH, '//*[@id="searchSubmit"]').click()
    sleep(2)

    books = driver.find_elements(By.CLASS_NAME, 'bookinfo')
    isbn13 = ''
    isbn10 = ''
    if len(books) > 0:
        try:
            isbn13 = books[0].find_element(By.XPATH, '//*[@id="isbn13"]').text.split(' ')[-1]
            isbn10 = books[0].find_element(By.XPATH, '//*[@id="isbn10"]').text.split(' ')[-1]
        except:
            pass
    driver.close()

    return isbn13, isbn10


def get_book_infos(link, genre):
    infos = {}
    try:
        # Open the book link and scrape the data
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        if link.startswith('https'):
            driver.get(link)
        else:
            driver.get(SITE + '/' + link)
        sleep(2)

        # Get title, subtitle
        title = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[1]/div[1]/h1').text
        title = title.split(':')  # In goodreads, the title is in the format "Book title: {title}"
        if len(title) > 1:
            title = title[-1].strip()
            subtitle = title[0]
        else:
            title = title[0]
            subtitle = ''
        infos['title'] = title
        infos['subtitle'] = subtitle

        # Get ISBN
        isbn13, isbn10 = getting_isbn(title)
        infos['isbn13'] = isbn13
        infos['isbn10'] = isbn10

        # Get author
        author = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[1]/h3/div/span[1]/a/span').text
        infos['authors'] = author

        # Get rating
        rating = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[2]/a/div[1]/div').text
        infos['average_rating'] = rating

        # Get rating count
        rating_count_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[2]/a/div[2]/div/span[1]')
        rating_count = rating_count_element.text if rating_count_element else '0'
        rating_count = int(rating_count.replace(',', ''))
        infos['ratings_count'] = rating_count

        # Get genre
        infos['categories'] = genre

        # Get description
        show_more_description = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div/button')
        # This button is not always present, so we need to check if it exists before clicking it
        if show_more_description:
            show_more_description.click()
            sleep(1)
        description = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[1]/div/div/span').text
        infos['description'] = description

        # Get thumbnail
        thumbnail = driver.find_element(By.XPATH, '//*[@id="coverImage"]').get_attribute('src')
        infos['thumbnail'] = thumbnail

        # Get number of pages
        num_pages = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/span[1]/span/div/p[1]').text
        num_pages = int(num_pages.split(' ')[0].replace(',', ''))  # In goodreads, the number of pages is in the format "{number} pages, Paperback"
        infos['num_pages'] = num_pages

        # Get published year
        published_year = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/span[1]/span/div/p[2]').text
        published_year = int(published_year.split(' ')[-1])  # In goodreads, the published year is in the format "Published day month, {year}"
        infos['published_year'] = published_year

        driver.close()

    except:
        pass

    return pd.DataFrame.from_dict(infos)

book_infos = pd.DataFrame(columns=['isbn13', 'isbn10', 'title', 'subtitle', 'authors', 'average_rating', 'ratings_count', 'categories', 'description', 'thumbnail', 'num_pages', 'published_year'])

for genre in GENRES:
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(SITE + '/' + 'genres' + '/' + genre)
    sleep(2)

    # Find the 'more {genre} books...' button and click it
    show_more = driver.find_element(By.XPATH, '//*[@id="bodycontainer"]/div[3]/div[1]/div[2]/div[2]/div[8]/div[1]/h2/a')
    show_more.click()
    sleep(2)

    # Get list of books
    books = driver.find_elements(By.CLASS_NAME, 'leftAlignedImage')

    with ThreadPoolExecutor(max_workers=5) as executor:
        threads = []
        for i, book in enumerate(books):
            # Get the link for each book and then start a thread to scrape its information
            link = book.get_attribute('href')
            threads.append(executor.submit(get_book_infos, link, genre)) 

        for future in threads:
            try:
                book_info = future.result()
                if not book_info.empty:
                    book_infos = pd.concat([book_infos, book_info], ignore_index=True)
            except:
                pass

    driver.close()

# Save the data to a CSV file
book_infos.to_csv('books.csv', index=False)