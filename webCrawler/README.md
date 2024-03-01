# To Run

```
source .venv/Scripts/activate # This crawler uses a different virtual environment from the rest of the django project
pip install -r requirements.txt

# docker operation isn't necessary for little JS scraping like the show spider, but I keep it here just in case.
docker pull scrapinghub/splash
docker run -it -p 8050:8050 --rm scrapinghub/splash

# in webCrawler/show
scrapy crawl ibdb
```
