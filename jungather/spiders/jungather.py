import re
from scrapy import Spider, Request
from jungather.items import JungatherItem

class jungather(Spider):
    name = "jungather"
    allowed_domains = ["www.okzyw.com"]
    start_urls = "http://www.okzyw.com/"
    base_url = "http://www.okzyw.com/{parameter}"

    def start_requests(self):
        url = "http://www.okzyw.com/?m=vod-index.html"
        yield Request(url, callback=self.list_parse)

    def list_parse(self, response):
        result = response.css(".xing_vb4 a::attr(href)").getall()
        for url in result:
            print("解析:"+ url)
            yield Request(self.base_url.format(parameter=url), \
                    callback=self.details_parse)
        next = response.css(".pages .pagelink_a")
        link = None
        for n in next:
            if n.css("a::text").get() == "下一页":
                link = response.urljoin(n.css("a::attr(href)").get())
                text = n.css("a::text").get()
                print("爬取" + text + ":" + link)
                break
        if link is not None:
            yield Request(url=link,callback=self.list_parse)

    def details_parse(self, response):
        result = response.css(".warp")
        item = JungatherItem()
        plot = re.compile('txt="(.*?)">')
        item["title"] = result.css(".vodh h2::text").get()
        item["status"] = result.css(".vodh span::text").get()
        videoinfo = result.css(".vodInfo li span::text").getall()
        item["alias"] = videoinfo[0]
        item["director"] = videoinfo[1]
        item["actor"] = videoinfo[2]
        item["videotype"] = videoinfo[3]
        item["area"] = videoinfo[4]
        item["language"] = videoinfo[5]
        item["released"] = videoinfo[6]
        item["length"] = videoinfo[7]
        item["update"] = videoinfo[8]
        item["plot"] = plot.findall(result.css(".cont").get())[0]
        plays = result.css("#2")
        temp = {}
        if plays is not None:
            for play in plays:
                temp[re.findall("(.*?)\$", play.css("li::text").get())[0]] = \
                        play.css("input::attr(value)").get()
        item["plays"] = temp
        downloads = result.css("#down_1")
        if downloads is not None:
            for download in downloads:
                temp[re.findall("(.*?)\$", download \
                        .css("li::text").get())[0]] = download \
                        .css("input::attr(value)").get()
        item["downloads"] = temp
        yield item
