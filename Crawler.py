import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager
import os
from Detector import detect
import DBHandler

default_directory = "/Users/lun/Desktop/ProjectX/paintings/"
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                         "AppleWebKit/537.1 (KHTML, like Gecko) "
                         "Chrome/22.0.1207.1 Safari/537.1"}


def parse_url(url, timeout=10):
    return BeautifulSoup(requests.get(url, headers=headers, timeout=timeout).text, "lxml")


def fetch_image(url, title, filename, count):
    try:
        # download the image
        img_url = parse_url(url).find("div", class_="artwork").find("img")["src"]
        img_data = requests.get(img_url, headers=headers)

        # store the image
        with open(filename, "wb") as f:
            f.write(img_data.content)
            count.value += 1
            print("No.{count} {title}".format(count=count.value, title=title))

    except requests.exceptions.Timeout:
        print("Timeout when download: {}".format(title))


def crawl(directory=default_directory, max_storage=1000):
    # specify directory to store paintings
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)

    # view paintings as grids
    max_page = max_storage / 20
    grids_soup = parse_url("https://artuk.org/discover/artworks/view_as/grid//page/" + str(max_page))
    all_li = grids_soup.find("ul", class_="listing-grid listing masonary-grid").find_all("li")

    try:
        # download paintings
        pool = Pool()
        count = Manager().Value("d", 0)

        for li in all_li:
            url = li.find("a")["href"]
            title_info = li.find("span", class_="title")

            # remove the date info if necessary
            if title_info.find("span", class_="date"):
                title_info.find("span", class_="date").extract()

            # title should not be longer than 50 characters
            title, filename = DBHandler.title_to_filename(title_info.get_text().strip())

            # only download those haven't been done face detection
            if not DBHandler.bbox_did_exist(title):
                pool.apply_async(fetch_image, args=(url, title, filename, count))
            else:
                print("Already exists: {}".format(title))

        pool.close()
        pool.join()
        print("Download finished.")

    except Exception as e:
        print("Error in download: {}".format(e))

    finally:
        detect(directory)


if __name__ == "__main__":
    crawl()
