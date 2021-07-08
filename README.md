# LINE Spider

This is a simple project for crawling news data from [LINE Fact Checker](https://fact-checker.line.me).

## Requirements

* python 3.X
* beautifulsoup4
* selenium
* tqdm

## Data Format

```
{
    "category": "...",
    "time": "2021/07/06 09:08",
    "label": "...",
    "text": "...",
    "url": "...",
    "verify_url": "..."
}
...
```

## Usage

```
python crawler.py --page=50 --size=20
```

* --page : the number of page to crawl
* --size : the number of news per page
* Note that the total number of news data you will crawl is equal to `page` x `size`.