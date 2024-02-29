import scrapy


class IbdbSpider(scrapy.Spider):
    name = "ibdb"
    allowed_domains = ["www.ibdb.com"]
    start_urls = ["https://www.ibdb.com/shows"]

    def parse(self, response):
        for show in response.css(".xt-iblock"):
            yield {
                "image": show.css(".iblock-image").attrib["style"][
                    len("background-image: url(") : -1
                ],
                "titile": show.css("i::text").get(),
                "href": show.css("a").attrib["href"],
            }
