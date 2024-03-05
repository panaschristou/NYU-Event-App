# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NyuEvent(scrapy.Item):
    id = scrapy.Field()
    href = scrapy.Field()

    title = scrapy.Field()
    location = scrapy.Field()
    open_date = scrapy.Field()
    availability = scrapy.Field()
    category = scrapy.Field()
    external_link = scrapy.Field()
    image_url = scrapy.Field()
    # not implemented fields
    description = scrapy.Field()
    close_date = scrapy.Field()
