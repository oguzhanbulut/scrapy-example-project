import html2text as html2text
import scrapy
from scrapy import Selector
from scrapy.http import HtmlResponse


class AstalegaleSpider(scrapy.Spider):
    name = 'astalegale'
    allowed_domains = ['astalegale.net']

    def start_requests(self):
        urls = [
            'https://www.astalegale.net/Immobili/Detail/B1921036',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        selectorHTML = Selector(response=response)
        title = selectorHTML.xpath('//h1[@class="cc-page-title"]/text()').extract()
        description = selectorHTML.xpath('//span[@data-pn-lotto-descrizione="val"]/text()').extract()
        latitude = selectorHTML.xpath('//input[@name="lat"]/@value').extract()
        longitude = selectorHTML.xpath('//input[@name="lng"]/@value').extract()
        price = selectorHTML.xpath('//span[@itemprop="price"]/@content').extract()

        yield {'title': title}
        yield {'description': description}
        yield {'latitude': latitude}
        yield {'longitude': longitude}
        yield {'price': price}

        converter = html2text.HTML2Text()
        converter.ignore_links = True

        cc_sidebar_section = selectorHTML.xpath('//aside[@class="cc-sidebar hidden-print"]').extract()
        cc_sidebar_response = HtmlResponse(url="sidebar", body=cc_sidebar_section[0], encoding='utf-8')
        selector_sidebar = Selector(response=cc_sidebar_response)
        cc_info_titles = selector_sidebar.xpath('//span[@class="cc-label"]/text()').extract()
        cc_info_texts = selector_sidebar.xpath('//span[@class="cc-text"]/text()').extract()
        qq = 0
        for cc_info_title in cc_info_titles:
            cc_info_text = converter.handle(cc_info_texts[qq]).strip()
            cc_info_title = converter.handle(cc_info_title).strip().replace(":", "")
            print("sidebar-" + cc_info_title + ": " + cc_info_text)
            yield {"sidebar-" + cc_info_title: cc_info_text}
            qq += 1


        cc_field_sections = selectorHTML.xpath('//div[@class="cc-section-info"]').extract()
        i = 0
        for cc_section in cc_field_sections:
            if i != 0:
                cc_section_response = HtmlResponse(url="info", body=cc_section, encoding='utf-8')
                selector_section = Selector(response=cc_section_response)
                section_title = selector_section.xpath('//h3[@class="cc-title"]/text()').extract()
                section_title = section_title[0].replace(" ", "")
                cc_field_titles = selector_section.xpath('//div[@class="cc-row"]//*[@class="cc-field-title"]').extract()
                cc_field_texts = selector_section.xpath('//div[@class="cc-row"]//*[@class="cc-field-text"]').extract()
                q = 0
                for cc_field_title in cc_field_titles:
                    cc_field_text = converter.handle(cc_field_texts[q]).strip()
                    cc_field_title = converter.handle(cc_field_title).strip()

                    print(section_title + "-" + cc_field_title + ": " + cc_field_text)
                    yield {section_title + "-" + cc_field_title: cc_field_text}
                    q += 1
            i += 1
