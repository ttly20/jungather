import re
from scrapy import Spider, Request
from jungather.items import JungatherItem

class okzyw(Spider):
    name = "okzyw"
    allowed_domains = ["www.okzyw.com"]
    base_url = "http://www.okzyw.com{parameter}"
    re_str = ".*?span>(.*?)</span>"
    re_video = "别名.*?span>(.*?)</span>.*?[\s\S]*" + \
            "导演.*?span>(.*?)</span>.*?[\s\S]*" + \
            "主演.*?span>(.*?)</span>.*?[\s\S]*" + \
            "类型.*?span>(.*?)<.*?[\s\S]*" + \
            "地区.*?span>(.*?)</span.*?[\s\S]*" + \
            "语言.*?span>(.*?)</span.*?[\s\S]*" + \
            "上映.*?span>(.*?)</span.*?[\s\S]*" + \
            "片长.*?span>(.*?)</span.*?[\s\S]*" + \
            "更新.*?span>(.*?)</span>"

    def start_requests(self):
        url = "http://www.okzyw.com/?m=vod-index.html"
        yield Request(url, callback=self.list_parse)

    def list_parse(self, response):
        result = response.css(".xing_vb4 a::attr(href)").getall()
        for url in result:
            print("解析:"+ url)
            yield Request(self.base_url.format(parameter=url), \
                    callback=self.details_parse)
            # break
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
            pass

    def details_parse(self, response):
        result = response.css(".warp")
        item = JungatherItem()
        item["poster"] = result.css(".lazy::attr(src)").get()
        item["title"] = result.css(".vodh h2::text").get()
        item["status"] = result.css(".vodh span::text").get()
        video = result.css(".vodinfobox").get()
        videoinfo = list(re.findall(self.re_video, video)[0])
        if videoinfo is not None:
            item["alias"] = videoinfo[0]
            item["director"] = videoinfo[1]
            item["actor"] = videoinfo[2]
            item["videotype"] = videoinfo[3]
            item["area"] = videoinfo[4]
            item["language"] = videoinfo[5]
            item["released"] = videoinfo[6]
            item["length"] = videoinfo[7] + "分钟"
            item["update"] = videoinfo[8]
        else:
            return
        item["plot"] = re.findall('txt="(.*?)">', result.css(".cont") .get())[0]
        plays = result.css("#2 ul li")
        temp = {}
        if plays is not None:
            for play in plays:
                temp[re.findall("(.*?)\$", play.css("li::text") \
                        .get())[0]] = play.css("input::attr(value)").get()
            print(temp)
        else:
            print("没有播放地址,跳过.")
            return
        item["plays"] = temp
        downloads = result.css("#down_1 ul li")
        d_temp = {}
        if downloads is not None:
            for download in downloads:
                d_temp[re.findall("(.*?)\$", download.css("li::text") \
                        .get())[0]] = download.css("input::attr(value)").get()
        item["downloads"] = d_temp
        if item["videotype"] != "福利片" or item["videotype"] != "伦理片":
            if item["videotype"] != "福利片 " or item["videotype"] != "伦理片 ":
                yield item
