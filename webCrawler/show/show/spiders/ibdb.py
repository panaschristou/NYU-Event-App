import scrapy


def itemPure(item):
    return item if item else ""


class IbdbSpider(scrapy.Spider):
    name = "ibdb"
    allowed_domains = ["www.ibdb.com"]
    start_urls = ["https://www.ibdb.com/shows"]

    def parse(self, response):
        for show in response.css(".xt-iblock"):
            sinfo = {
                "image_url": itemPure(
                    show.css(".iblock-image").attrib["style"][
                        len("background-image: url(") : -1
                    ]
                ),
                "titile": itemPure(show.css("i::text").get()),
                "href": itemPure(show.css("a").attrib["href"]),
            }
            if sinfo["href"].startswith("/broadway-production/"):
                yield scrapy.Request(
                    "https://www.ibdb.com/" + sinfo["href"],
                    callback=self.parseBroadwayProduction,
                    meta={"sinfo": sinfo},
                )
            elif sinfo["href"].startswith("/tour-production/"):
                yield scrapy.Request(
                    "https://www.ibdb.com/" + sinfo["href"],
                    callback=self.parseTourProduction,
                    meta={"sinfo": sinfo},
                )

    def parseBroadwayProduction(self, response):
        sinfo = response.meta["sinfo"]

        sinfo["category"] = response.css(".tag-block-compact i::text").getall()
        sinfo["external_links"] = []
        for el in response.css(".prod-links a"):
            sinfo["external_links"].append(
                {
                    "text": itemPure(el.css("::text")[-1].get()).strip(),
                    "href": el.attrib["href"] if "href" in el.attrib else "",
                }
            )

        sinfo["open_date"] = itemPure(response.css(".l5 .xt-main-title::text").get())
        sinfo["close_date"] = itemPure(
            response.css(".vertical-divider .xt-main-title::text").get()
        )
        sinfo["location"] = response.css("#venues a::text").get()
        location_href = response.css("#venues a")
        sinfo["location_href"] = (
            location_href.attrib["href"] if "href" in location_href.attrib else ""
        )
        yield sinfo

    def parseTourProduction(self, response):
        sinfo = response.meta["sinfo"]

        sinfo["category"] = response.css(".tag-block-compact i::text").getall()
        sinfo["external_links"] = []
        for el in response.css(".prod-links a"):
            sinfo["external_links"].append(
                {
                    "text": itemPure(el.css("::text")[-1].get()).strip(),
                    "href": el.attrib["href"] if "href" in el.attrib else "",
                }
            )

        sinfo["instances"] = []
        for instance in response.css(
            "#currenttourstops .row:not(.hide-on-small-and-down)"
        ):
            sinfo["instances"].append(
                {
                    "location_href": (
                        instance.css("a").attrib["href"]
                        if "href" in instance.css("a").attrib
                        else ""
                    ),
                    "location": itemPure(instance.css("a::text").get()),
                    "engagement_dates": itemPure(instance.css(".m4::text").get()),
                }
            )
        yield sinfo
