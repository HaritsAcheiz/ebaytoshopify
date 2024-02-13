import asyncio
import re
import urllib
from typing import List
from math import ceil
import pandas as pd
from httpx import Client, AsyncClient, Timeout
from selectolax.parser import HTMLParser
from dataclasses import dataclass, field


@dataclass
class Product:

    links: List[str] = field(default_factory=lambda: [])


@dataclass
class Scraper(Product):

    base_url: str = 'https://www.ebay.com'

    proxies: List[str] = field(default_factory=lambda: [
        '172.93.142.88:8800',
        '172.93.139.182:8800',
        '192.126.191.64:8800',
        '172.93.139.243:8800',
        '192.126.190.242:8800',
        '192.126.191.106:8800',
        '172.93.142.97:8800',
        '192.126.191.192:8800',
        '192.126.190.93:8800',
        '192.126.191.254:8800'
    ])

    uas: List[str] = field(
        default_factory=lambda: [
            'insomnia / 2023.5.8',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36'
        ])

    ip_index: int = 0
    ua_index: int = 0
    page_range: int = 0

    # def get_page_range(self):
    #
    #     ip = self.proxies[2]
    #     formated_proxy = {
    #         "http://": f"http://{ip}",
    #         "https://": f"http://{ip}"
    #     }
    #     ua = self.uas[0]
    #     headers = {
    #         'user-agent': ua,
    #         'dnt': '1'
    #     }
    #     endpoint = f'/b/Battery-Operated-Toys/19072/bn_1926973?LH_BIN=1&LH_ItemCondition=1000&mag=1&rt=nc&_sop=16'
    #     url = urllib.parse.urljoin(self.base_url, endpoint)
    #
    #     with Client(headers=headers, proxies=formated_proxy) as client:
    #         response = client.get(url)
    #         if response != 200:
    #             response.raise_for_status()
    #
    #     tree = HTMLParser(response.text)
    #     product_count_str = tree.css_first('h2.srp-controls__count-heading').text(strip=True)
    #     product_count_int = int(''.join(re.findall(r'\d', product_count_str)))
    #     page_range = ceil(product_count_int / 48)
    #     return page_range

    async def fetch(self, url, message, ip, ua, limit):

        formated_proxy = {
            "http://": f"http://{ip}",
            "https://": f"http://{ip}"
        }

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Host': 'www.ebay.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
            'TE': 'trailers',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': ua
        }

        timeout = Timeout(30.0, read=None)
        async with AsyncClient(headers=headers, timeout=timeout, proxies=formated_proxy, follow_redirects=False) as aclient:
            async with limit:
                response = await aclient.get(url)
                if limit.locked():
                    await asyncio.sleep(5)
        if response.status_code == 200:
            result = response
            print(message)
        else:
            print(ip)
            print(ua)
            response.raise_for_status()

        return result


    async def fetch_all_product_page(self, page_range):

        tasks = []
        for page in range(1, page_range + 1):
            if self.ip_index > 5:
                self.ip_index = 0
            if self.ua_index > 2:
                self.ua_index = 0
            ua = self.uas[self.ua_index]
            ip = self.proxies[self.ip_index]
            endpoint = f'/b/Battery-Operated-Toys/19072/bn_1926973?LH_BIN=1&LH_ItemCondition=1000&mag=1&rt=nc&_pgn={str(page)}_sop=16'
            url = urllib.parse.urljoin(self.base_url, endpoint)
            limit = asyncio.Semaphore(6)
            message = f'Fetching {str(page)} of {str(page_range)}'
            task = asyncio.create_task(self.fetch(url, limit=limit, ip=ip, ua=ua, message=message))
            self.ip_index += 1
            self.ua_index += 1
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        return responses

    def parse_product_links(self, responses):

        product_links = []
        for response in responses:
            tree = HTMLParser(response.text)
            if tree.css_first('h2.srp-controls__count-heading'):
                products = tree.css('ul.b-list__items_nofooter > li')
                if len(products) == 0:
                    products = tree.css(
                        'ul.brwrvr__item-results.brwrvr__item-results--gallery > li.brwrvr__item-card')
                for product in products:
                    product_link = product.css_first('a').attributes.get('href')
                    product_links.append(product_link)

        print(f'{len(product_links)} product links collected')

        return product_links


if __name__ == '__main__':

    scraper = Scraper()
    # page_range = scraper.get_page_range()
    page_range = 209
    responses = asyncio.run(scraper.fetch_all_product_page(page_range))
    result = scraper.parse_product_links(responses)
    print(f'result: {result}')
    print(f'unique result: {len(set(result))}')
    print(f'len result: {len(result)}')
