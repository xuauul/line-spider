import json
import argparse

from tqdm import tqdm
from time import sleep, strptime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import FirefoxOptions


class LineNewsSpider:
    def __init__(self, page, size):
        self.page = page
        self.size = size
        self.url = f"https://fact-checker.line.me/category?type=verified&params=%7B%22size%22:{size}%7D"

    def run(self):
        filename = f"data/line_news_{self.page * self.size}"

        with open(filename + ".json", 'w', encoding="utf-8") as fout:
            for data in tqdm(self.get_data(), total=self.page * self.size):
                fout.write(json.dumps(data, ensure_ascii=False) + '\n')

        # sort by time
        with open(filename + ".json", 'r', encoding="utf-8") as fin, \
             open(filename + "_sort.json", 'w', encoding="utf-8") as fout:
             items = [json.loads(line) for line in fin]
             items.sort(key=lambda x: strptime(x["time"], "%Y/%m/%d %H:%M"), reverse=True)
             for data in items:
                 fout.write(json.dumps(data, ensure_ascii=False) + '\n')

    def get_data(self):
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        opts.add_argument("start-maximized")
        opts.add_argument("disable-infobars")
        opts.add_argument("--disable-extensions")
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-application-cache')
        opts.add_argument('--disable-gpu')
        opts.add_argument("--disable-dev-shm-usage")
        with webdriver.Firefox(options=opts) as driver:
            driver.get(self.url)
            for _ in range(self.page):
                sleep(10)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                categories = [tr.findChildren("td")[2].string for tr in soup.select(".table-row")]
                labels = [tag.string for tag in soup.select(".tableTop10-tag")]

                assert len(categories) == self.size and len(labels) == self.size, (len(categories), len(labels))

                for i in range(self.size):
                    try:
                        driver.find_elements_by_class_name("tableTop10-contentRight")[i].click()
                        sleep(0.5)
                    except Exception as err:
                        print(err)
                        continue
                    try:
                        text, time, verify_url = self.get_one_page_content(driver.page_source)
                    except Exception as err:
                        print(err)
                    else:
                        yield {
                            "category": categories[i],
                            "time": time,
                            "label": labels[i],
                            "text": text,
                            "url": driver.current_url,
                            "verify_url": verify_url
                        }
                    finally:
                        driver.back()
                        sleep(0.5)

                driver.find_element_by_class_name("icon-pagination-right").click()
            driver.quit()

    def get_one_page_content(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.select(".articleStory-title")[0].string
        time = soup.select(".articleStory-subdescription")[0].string
        time = ' '.join(time.split()[1:])
        verify_url = soup.select(".articleWithThumbnail-right")[0].find("a")["href"]

        return text, time, verify_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", type=int)
    parser.add_argument("--size", type=int)
    args = parser.parse_args()

    spider = LineNewsSpider(args.page, args.size)
    spider.run()
