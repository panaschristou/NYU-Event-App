# To Run

```
source .venv/Scripts/activate # This crawler uses a different virtual environment from the rest of the django project
pip install -r requirements.txt

docker pull scrapinghub/splash
docker run -it -p 8050:8050 --rm scrapinghub/splash

# in webCrawler/nyu
scrapy crawl nyuevents
```

