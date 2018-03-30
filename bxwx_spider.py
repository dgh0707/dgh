# -*- coding: utf-8 -*-
import scrapy
from bxwx.items import BxwxItem
import os
class BxwxSpiderSpider(scrapy.Spider):
    name = 'bxwx_spider'
    allowed_domains = ['www.bxwx9.org']
    start_urls = ['https://www.bxwx9.org/modules/article/index.php?fullflag=1']

##    def start_requests(self):
##        urls = [
##            'https://www.bxwx9.org/modules/article/index.php?fullflag=1',
##            'https://www.bxwx9.org/modules/article/index.php?fullflag=1&page=2',
##        ]
##        for url in urls:
##            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        items=BxwxItem()
        #获取总页数，回调执行响应函数
        num=response.css('a.last::text').extract_first()
        if num:
            for page in range(2,int(num)+1):
                url='https://www.bxwx9.org/modules/article/index.php?fullflag=1&page='+str(page)
                yield scrapy.Request(url,callback=self.parse)
        #获取每本书的书名和url
        res=response.css('table.grid tr')[1:]
        if res:
            for tr in res:
                book_name=tr.css('td.odd a::text').extract_first()
                book_url=tr.css('td.odd a::attr(href)').extract_first().replace('info','').replace('.htm','/index.html')
                #每获取到一本书的url回调一次
                yield scrapy.Request(book_url,callback=self.parse)
                
                items['book_name']=book_name
                items['book_url']=book_url
                yield items
        #获取章节url
        articles=response.css('div.TabCss dd')
        if articles:
            for dd in articles:
                article_url=dd.css('a::attr(href)').extract_first()
                article_url=response.url.replace('index.html',article_url)
                #每获取到一个章节回调一次
                yield scrapy.Request(article_url,callback=self.parse)
        #下载小说
        info=response.css('div#info')
        if info:
            article_name=response.css('div#title::text').extract_first()
            content=response.css('div#content').xpath('string(.)').extract_first()
            book_name=info.css('a')[1].css('::text').extract_first()
            items['article_name']=article_name
            items['content']=content
            if '全集' in book_name:
                items['book_name']=book_name.split('全集')[0]
            else:
                items['book_name']=book_name.split('TXT')[0]
            yield items
            
        

