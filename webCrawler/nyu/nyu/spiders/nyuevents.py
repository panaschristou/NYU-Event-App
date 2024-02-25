import json
import scrapy
from scrapy_splash import SplashRequest

from ..items import NyuEvent

event_detail_script = """
    function main(splash, args)  
      splash:go(args.url)
    
    #   while not splash:select(".promo-image").attrib["src"] do
    #     splash:wait(0.2)
    #     print("waiting...")
    #   end
      
      return splash:html()
    end
"""


class NyueventsSpider(scrapy.Spider):
    name = "nyuevents"
    allowed_domains = ["events.nyu.edu"]

    def start_requests(self):
        yield scrapy.Request(
            """
    https://events.nyu.edu/live/calendar/view/all/groups/discounted-tickets?syntax=%3Cwidget%20type%3D%22events_calendar%22%3E%3Carg%20id%3D%22modular_true%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22mini_cal_heat_map%22%3Efalse%3C%2Farg%3E%3Carg%20id%3D%22search_all_events_only%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22search_all_events_only%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22include_featured_content%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22thumb_width%22%3E430%3C%2Farg%3E%3Carg%20id%3D%22thumb_height%22%3E300%3C%2Farg%3E%3Carg%20id%3D%22hide_repeats%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_groups%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_locations%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_tags%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22feed_base_path%22%3Ehttp%3A%2F%2Fwww.nyu.edu%2Ffeeds%2Fevents%3C%2Farg%3E%3C%2Fwidget%3E
    """
        )

        yield scrapy.Request(
            """
    https://events.nyu.edu/live/calendar/view/all/groups/discounted-tickets?syntax=%3Cwidget%20type%3D%22events_calendar%22%3E%3Carg%20id%3D%22modular_true%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22mini_cal_heat_map%22%3Efalse%3C%2Farg%3E%3Carg%20id%3D%22search_all_events_only%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22search_all_events_only%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22include_featured_content%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22thumb_width%22%3E430%3C%2Farg%3E%3Carg%20id%3D%22thumb_height%22%3E300%3C%2Farg%3E%3Carg%20id%3D%22hide_repeats%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_groups%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_locations%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_tags%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22feed_base_path%22%3Ehttp%3A%2F%2Fwww.nyu.edu%2Ffeeds%2Fevents%3C%2Farg%3E%3C%2Fwidget%3E&page=2
    """
        )

    def parse(self, response):
        events = json.loads(response.text)["events"]
        for date, eventList in events.items():
            for event in eventList:
                einfo = NyuEvent(
                    id=event["id"],
                    href=event["href"],
                    open_date=date,
                    title=event["title"],
                    availability=event["status"],
                )
                yield SplashRequest(
                    "https://events.nyu.edu/" + event["href"],
                    callback=self.parse_event,
                    meta={"einfo": einfo},
                    args={"lua_source": event_detail_script},
                )

    def parse_event(self, response):
        einfo = response.meta["einfo"]
        locationElements = response.css(".lw_event_location *::text").getall()
        einfo["location"] = "".join(locationElements).replace("Location: ", "").strip()
        einfo["category"] = response.css(
            ".lw_cal_event_tags .lw_cal_app_link::text"
        ).getall()
        external_link = response.css("#lw_cal_event_rightcol .log-in-to-buy").attrib[
            "href"
        ]
        einfo["external_link"] = external_link if external_link else ""
        image = response.css("img.promo-image").attrib["src"]
        einfo["image_url"] = image if image else ""
        yield einfo
