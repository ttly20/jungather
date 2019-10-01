# -*- coding: utf-8 -*-
import re
from scrapy import Spider, Request
from jungather.items import JungatherItem


class ZdzywSpider(Spider):
    name = 'zdzyw'
    allowed_domains = ['www.zuidazy1.net']
    base_url = 'http://www.zuidazy1.net{}'
    item = JungatherItem()
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
        url = 'http://www.zuidazy1.net'
        yield Request(url, callback=self.list_parse)


    def list_parse(self, response):
        result = response.css('body')
        list = result.css('.xing_vb .xing_vb4 a::attr(href)').getall()
        if list is not None:
            for link in list:
                url = self.base_url.format(link)
                print('解析: ' + url)
                yield Request(url, callback=self.details_parse)
                break
        next = response.css('.pagelink_a')
        for n in next:
            if n.css('a::text') == '下一页':
                link = response.urljoin(n.css('a::attr(href)').get())
                text = n.css('a::text').get()
                break
        if link is not None:
            print('爬取' + text + ': ' + link)
            yield Request(link, callback=self.list_parse)


    def details_parse(self, response):
        result = response.css('body')
        self.item['title'] = result.css('.vodh h2::text').get()
        self.item['status'] = result.css('.vodh span::text').get()
        self.item['poster'] = result.css('.vodImg img::attr(src)').get()
        infobox = result.css('.vodinfobox').get()
        info = list(re.findall(self.re_video, infobox)[0])
        if info is not None:
            self.item["alias"] = info[0]
            self.item["director"] = info[1]
            self.item["actor"] = info[2]
            self.item["videotype"] = info[3]
            self.item["area"] = info[4]
            self.item["language"] = info[5]
            self.item["released"] = info[6]
            self.item["length"] = info[7] + "分钟"
            self.item["update"] = info[8]
        else:
            return
        plays = result.css("#play_1 ul li")
        temp = {}
        if plays is not None:
            for play in plays:
                temp[re.findall("(.*?)\$", play.css("li::text") \
                        .get())[0]] = play.css("input::attr(value)").get()
        else:
            print("没有播放地址,跳过.")
            return
        self.item["plays"] = temp
        downloads = result.css("#down_1 ul li")
        d_temp = {}
        if downloads is not None:
            for download in downloads:
                d_temp[re.findall("(.*?)\$", download.css("li::text") \
                        .get())[0]] = download.css("input::attr(value)").get()
        self.item["downloads"] = d_temp
        if self.item["videotype"] != "福利片" or self.item["videotype"] != "伦理片":
            if self.item["videotype"] != "福利片 " or self.item["videotype"] != "伦理片 ":
                yield self.item

