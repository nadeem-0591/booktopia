import csv
import re
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time 
file_path = r"C:\Users\shaik\Downloads\input_list.csv"

driver = webdriver.Chrome()

book_data = []

try:
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)

        for _ in range(101):
            row = next(reader)
            isbn_number = row['ISBN13']

            url = f"https://www.booktopia.com.au/ebook/{isbn_number}.html"
            driver.get(url)

            time.sleep(5)  

            try:
                json_element = driver.find_element(By.XPATH, '//script[@id="__NEXT_DATA__"]')
                json_data = json.loads(json_element.get_attribute('textContent'))

                isbn10 = json_data.get('props', {}).get('pageProps', {}).get('product', {}).get('isbn10', 'ISBN10 not found')

                number_of_pages_match = re.search(r"'numberOfPages': (\d+)", str(json_data))
                number_of_pages = int(number_of_pages_match.group(1)) if number_of_pages_match else "Number of Pages not found"

            except NoSuchElementException:
                print("Error extracting JSON data.")
                continue

            try:
                json_elements = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
                for json_element in json_elements:
                    json_data = json_element.get_attribute('textContent')


                    try:
                        title_match = re.search(r'"name":"(.*?)"', json_data)
                        title = title_match.group(1) if title_match else "Title not found"
                    except Exception as e:
                        title = "Title not found"

    
                    try:
                        author_match = re.search(r'"author":.*?"name":"(.*?)"', json_data)
                        author = author_match.group(1) if author_match else "Author not found"
                    except Exception as e:
                        author = "Author not found"

                    try:
                        publisher_match = re.search(r'"publisher":.*?"name":"(.*?)"', json_data)
                        publisher = publisher_match.group(1) if publisher_match else "Publisher not found"
                    except Exception as e:
                        publisher = "Publisher not found"

                    try:
                        published_date_match = re.search(r'"datePublished":"(.*?)"', json_data)
                        published_date = published_date_match.group(1) if published_date_match else "Published date not found"
                    except Exception as e:
                        published_date = "Published date not found"

                    
                    try:
                        price_match = re.search(r'"offers":.*?"price":(\d+\.\d+)', json_data)
                        price = price_match.group(1) if price_match else "Price not found"
                    except Exception as e:
                        price = "Price not found"

                    try:
                        rrp_price_element = driver.find_element(By.XPATH, '//div[@id="BuyBox_product-version__uw1et"]//p[@class="MuiTypography-root MuiTypography-body1 mui-style-vrqid8"]/span[contains(@class, "strike")]')
                        rrp_price = rrp_price_element.text.strip() if rrp_price_element else "RRP price not found"
                    except NoSuchElementException:
                        rrp_price = "RRP price not found"

                    try:
                        book_type_element = driver.find_element(By.XPATH, '(//div[contains(@class, "MuiBox-root") and contains(@class, "mui-style-1ebnygn")]//p[contains(@class, "MuiTypography-body1")])[2]')
                        book_type_text = book_type_element.text.strip()
                        book_type_match = re.search(r'(.*?)\|', book_type_text)
                        book_type = book_type_match.group(1).strip() if book_type_match else "Book Type not found"
                    except NoSuchElementException:
                        book_type = "Book Type not found"

                    book_data.append({
                        'Title of the Book': title,
                        'Author/s': author,
                        'Book type': book_type,
                        'Original Price (RRP)': rrp_price,
                        'Discounted price': price,
                        'ISBN-10': isbn10,
                        'Published Date': published_date,
                        'Publisher': publisher,
                        'No. of Pages': number_of_pages
                    })

            except NoSuchElementException as e:
                print("Error extracting information:", e)

except FileNotFoundError:
    print("File not found or path is incorrect.")
except Exception as e:
    print("An error occurred:", e)
finally:
    driver.quit()

df = pd.DataFrame(book_data)

df.to_csv('book_details.csv', index=False)
