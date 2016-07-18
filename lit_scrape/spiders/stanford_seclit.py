import re
import logging

import scrapy
from scrapy.loader import ItemLoader


class LitigationSpider(scrapy.Spider):
    name = 'seclit'
    base_url = 'http://securities.stanford.edu/'
    start_urls = [base_url + 'filings.html?page=1',]

    def parse(self, response):
        for row in self.parse_table(response):
            yield row

        next_url = response.url
        logging.info("LIT: Serving up url: %s", next_url)
        p_opt = re.search('page=(\d+|\d+.0)', next_url, re.I)
        if p_opt and int(p_opt.group(1)) < 250:
            next_num = "page={}".format(int(p_opt.group(1))+1)
            next_url = next_url.replace(p_opt.group(0), next_num)
            # do not go past last one
            last = '//*[@id="records"]/div[2]/ul/li[last()]/a'
            last_tag = response.xpath(last).extract()[0]
            if p_opt.group(0) not in last_tag:
                logging.info("LIT: next url coming up! %s", next_url)
                yield scrapy.Request(next_url, self.parse)
            else:
                logging.error("LIT: Found next number(%s) in last tag (%s)",
                              next_num, last_tag)
        else:
            logging.error("LIT: No page option in (%s) or > 250 (%r)",
                          next_url, p_opt)


    def parse_table(self, response):
        """Returns the request object for the next issue or []."""
        # table: //div[@id="records"]/table/tbody/tr
        x = '//div[@id="records"]/table/tbody/tr[contains(@onclick,"filings-case.html")]/@onclick'
        # try:
        for row in response.xpath(x).extract():
            id_rgx = re.search('id=\d+', row, re.I)
            if id_rgx:
                lit_url = self.base_url + 'filings-case.html?' + id_rgx.group(0)
                yield scrapy.Request(lit_url, self.parse_lawsuit)

    def parse_lawsuit(self, response):
        l = ItemLoader(item={'url': response.url}, response=response)
        l.add_xpath('lit_name', '//*[@id="fic"]/div[1]/h4/text()')
        l.add_xpath('status', '//*[@id="summary"]/p[1]/text()')
        l.add_xpath('company', '//*[@id="company"]/div[1]/h4/text()')
        l.add_xpath('sector', '//*[@id="company"]/div[2]/div[1]/text()')
        l.add_xpath('industry', '//*[@id="company"]/div[2]/div[2]/text()')
        l.add_xpath('hq_location', '//*[@id="company"]/div[2]/div[3]/text()')
        l.add_xpath('ticker', '//*[@id="company"]/div[3]/div[1]/text()')
        l.add_xpath('market', '//*[@id="company"]/div[3]/div[2]/text()')
        l.add_xpath('market_status', '//*[@id="company"]/div[3]/div[3]/text()')
        l.add_xpath('court', '//*[@id="fic"]/div[2]/div[1]/text()')
        l.add_xpath('docket', '//*[@id="fic"]/div[2]/div[2]/text()')
        l.add_xpath('judge', '//*[@id="fic"]/div[2]/div[3]/text()')
        l.add_xpath('date_filed', '//*[@id="fic"]/div[3]/div[1]/text()')
        l.add_xpath('class_start', '//*[@id="fic"]/div[3]/div[2]/text()')
        l.add_xpath('class_end', '//*[@id="fic"]/div[3]/div[3]/text()')
        l.add_xpath('description', '//*[@id="summary"]/div[3]/div/text()')
        return l.load_item()
