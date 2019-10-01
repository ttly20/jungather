# -*- coding: utf-8 -*-
import re
from scrapy import Spider, Request
from jungather.items import JungatherItem


class YjzywSpider(Spider):
    name = 'yjzyw'
    allowed_domains = ['www.yongjiuzy.cc']
    base_url = 'http://www.yongjiuzy.cc{}'
    item = JungatherItem()


    def start_requests(self):
        url = 'http://www.yongjiuzy.cc'
        yield Request(url, callback=self.list_parse)


    def list_parse(self, response):
        items = response.css('.tbody tr')
        for item in items:
            url = self.base_url.format(item.css('td[class] a::attr(href)') \
                    .get())
            print('解析: ' + url)
            yield Request(url, callback=self.details_parse)
            # break
        next = response.css('.page_num')
        link = None
        for n in next:
            if n.css('a::text').get() == '下一页':
                link = response.urljoin(n.css('a::attr(href)').get())
                text = n.css('a::text').get()
                print('爬取' + text + ': ' + link)
                break
        if link is not None:
            yield Request(url=link, callback=self.list_parse)


    def details_parse(self, response):
        result = response.css('body')

        ## Poster parse
        self.item['poster'] = result.css('.videoPic img::attr(src)').get()
        
        ## Info parse
        info = {}
        details = result.css('.videoDetail').get()
        rx_value = '-->(.*?)<!--.*?<'
        values = re.findall(rx_value, details)
        if values is not None:
            self.item['title'] = values[0]
            self.item['alias'] = values[1]
            self.item['status'] = values[2]
            self.item['actor'] = values[3]
            self.item['director'] = values[4]
            self.item['videotype'] = values[5]
            self.item['language'] = values[7]
            self.item['area'] = values[8]
            self.item['released'] = values[10]
            self.item['update'] = values[11]

        ## Plot parse
        plot = result.css('.boxmovie .contentNR .movievod p::text').get()
        self.item['plot'] = plot

        ## Play URL parse
        plays = {}
        pl = result.css('.movievod ul li')
        for index in range(len(pl)):
            text = pl[index].css('a span::text').get()
            url = pl[index].css('a::text').get()
            if url is not None:
                if re.findall('(.*?\.m3u8)', url):
                    plays[re.findall('(.*?)\$', text)[0]] = url
        self.item['plays'] = plays
        if self.item["videotype"] != "福利片" or self.item["videotype"] != "伦理片":
            if self.item["videotype"] != "福利片 " or self.item["videotype"] != "伦理片 ":
                yield self.item
