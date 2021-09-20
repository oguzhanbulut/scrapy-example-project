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
        # page = response.url.split("/")[-1]
        # filename = f'pages/{page}.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log(f'Saved file {filename}')
        selectorHTML = Selector(response=response)
        title = selectorHTML.xpath('//h1[@class="cc-page-title"]/text()').extract()
        description = selectorHTML.xpath('//span[@data-pn-lotto-descrizione="val"]/text()').extract()
        latitude = selectorHTML.xpath('//input[@name="lat"]/@value').extract()
        longitude = selectorHTML.xpath('//input[@name="lng"]/@value').extract()
        price = selectorHTML.xpath('//span[@itemprop="price"]/@content').extract()
        esito = selectorHTML.xpath('//span[@class="cc-text cc-text-esito"]/text()').extract()
        auction_date = selectorHTML.xpath('//*[@id="cc-wrapper"]//aside/section[1]/div[3]/span[2]/text()').extract()

        cc_field_sections = selectorHTML.xpath('//div[@class="cc-section-info"]').extract()
        i = 0
        for cc_section in cc_field_sections:
            if i != 0:
                cc_section_response = HtmlResponse(url="local", body=cc_section, encoding='utf-8')
                selector_section = Selector(response=cc_section_response)
                section_title = selector_section.xpath('//h3[@class="cc-title"]/text()').extract()
                section_title = section_title[0].replace(" ", "")
                cc_field_titles = selector_section.xpath('//div[@class="cc-row"]//*[@class="cc-field-title"]').extract()
                cc_field_texts = selector_section.xpath('//div[@class="cc-row"]//*[@class="cc-field-text"]').extract()
                q = 0
                for cc_field_title in cc_field_titles:
                    converter = html2text.HTML2Text()
                    converter.ignore_links = True
                    cc_field_text = converter.handle(cc_field_texts[q]).strip()
                    cc_field_title = converter.handle(cc_field_title).strip()

                    print(section_title + "-" + cc_field_title + ": " + cc_field_text)
                    yield {section_title + "-" + cc_field_title: cc_field_text}
                    q += 1
            i += 1

        yield {'title': title}
        yield {'description': description}
        yield {'latitude': latitude}
        yield {'longitude': longitude}
        yield {'price': price}
        yield {'esito': esito}
        yield {'auction_date': auction_date}
