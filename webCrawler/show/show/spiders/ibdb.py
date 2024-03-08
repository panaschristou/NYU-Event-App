import scrapy


def itemPure(item):
    return item if item else ""


class IbdbSpider(scrapy.Spider):
    name = "ibdb"
    start_urls = ["https://www.ibdb.com/shows"]

    def parse(self, response):
        for show in response.css(".xt-iblock"):
            sinfo = {
                "image_url": itemPure(
                    show.css(".iblock-image").attrib["style"][
                        len("background-image: url(") : -1
                    ]
                ),
                "title": itemPure(show.css("i::text").get()),
                "href": itemPure(show.css("a").attrib["href"]),
            }
            if sinfo["href"].startswith("/broadway-production/"):
                yield scrapy.Request(
                    "https://www.ibdb.com/" + sinfo["href"],
                    callback=self.parseBroadwayProduction,
                    meta={"sinfo": sinfo},
                )
            # elif sinfo["href"].startswith("/tour-production/"):
            #     yield scrapy.Request(
            #         "https://www.ibdb.com/" + sinfo["href"],
            #         callback=self.parseTourProduction,
            #         meta={"sinfo": sinfo},
            #     )

    def parseBroadwayProduction(self, response):
        sinfo = response.meta["sinfo"]

        sinfo["category"] = response.css(
            ".hide-on-med-and-up .tag-block-compact i::text"
        ).getall()
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
            response.css(
                ".xt-info-block>.wrapper:nth-child(1) .col:nth-child(2) .xt-main-title::text"
            ).get()
        )
        if (
            len(sinfo["external_links"]) > 0
            and "broadway.org" in sinfo["external_links"][0]["href"]
        ):
            yield scrapy.Request(
                sinfo["external_links"][0]["href"],
                callback=self.parseBroadway,
                meta={"sinfo": sinfo},
            )
        else:
            yield sinfo

    def parseBroadway(self, response):
        sinfo = response.meta["sinfo"]
        location = response.css(".col-lg-6.col-md-9 p")
        location = location.css("a::text,::text").getall()[:3]
        location = list(map(str.strip, location))
        sinfo["location"] = ", ".join(location)
        sinfo["description"] = "".join(response.css(".black-text p::text").getall())
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
