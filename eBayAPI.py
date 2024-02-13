import json

from httpx import Client
from dataclasses import dataclass

@dataclass
class Core:
    accessToken: str = None

    def getAccessToken(self):

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic bXVoYW1tYWQtYXBwa2V5czEtUFJELTE5NWY2Zjg5MC03ZTRiNWU1YjpQUkQtOTVmNmY4OTA5ZGZkLWI1M2YtNGRhMi04ZTc0LTk2Y2U='
        }

        with Client(headers=headers) as client:
            response = client.post('https://api.ebay.com/identity/v1/oauth2/token', data='grant_type=client_credentials&scope=https%3A%2F%2Fapi.ebay.com%2Foauth%2Fapi_scope')

        if response.status_code != 200:
            response.raise_for_status()

        self.accessToken = response.json()


    def find_items_by_category(self):

        url = 'https://svcs.ebay.com/services/search/FindingService/v1'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
            'Content-Type': 'application/xml',
            'X-EBAY-SOA-SECURITY-APPNAME': 'PerryCha-TrendTim-PRD-fea9be394-87a4e7c3',
            'X-EBAY-SOA-OPERATION-NAME': 'findItemsByCategory'
        }
        xml = """
        <?xml version="1.0" encoding="utf-8"?>
        <findItemsByCategoryRequest xmlns="http://www.ebay.com/marketplace/search/v1/services">
            <!-- Call-specific Input Fields -->
            <aspectFilter> AspectFilter
                <aspectName> string </aspectName>
                <aspectValueName> string </aspectValueName>
                <!-- ... more aspectValueName values allowed here ... -->
            </aspectFilter>
            <!-- ... more aspectFilter nodes allowed here ... -->
            <categoryId> 145944 </categoryId>
            <!-- ... more categoryId values allowed here ... -->
            <domainFilter> DomainFilter
                <domainName> string </domainName>
                <!-- ... more domainName values allowed here ... -->
            </domainFilter>
            <!-- ... more domainFilter nodes allowed here ... -->
            <itemFilter> ItemFilter
                <name> ItemFilterType </name>
                <paramName> token </paramName>
                <paramValue> string </paramValue>
                <value> string </value>
                <!-- ... more value values allowed here ... -->
            </itemFilter>
            <!-- ... more itemFilter nodes allowed here ... -->
            <outputSelector> OutputSelectorType </outputSelector>
            <!-- ... more outputSelector values allowed here ... -->
            <!-- Standard Input Fields -->
            <affiliate> Affiliate
                <customId> string </customId>
                <geoTargeting> boolean </geoTargeting>
                <networkId> string </networkId>
                <trackingId> string </trackingId>
            </affiliate>
            <buyerPostalCode> string </buyerPostalCode>
            <paginationInput> PaginationInput
                <entriesPerPage> int </entriesPerPage>
                <pageNumber> int </pageNumber>
            </paginationInput>
            <sortOrder> SortOrderType </sortOrder>
        </findItemsByCategoryRequest>
        """

        payload ="""
        <findItemsByCategoryRequest xmlns="http://www.ebay.com/marketplace/search/v1/services">
            <categoryId>145944</categoryId>
            <itemFilter>
                <name>Condition</name>
                <value>New</value>
            </itemFilter>
            <itemFilter>
                <name>ListingType</name>
                <value>AuctionWithBIN</value>
                <value>FixedPrice</value>
            </itemFilter>
            <paginationInput>
                <entriesPerPage>100</entriesPerPage>
                <pageNumber>100</pageNumber>
            </paginationInput>
            <sortOrder>PricePlusShippingHighest</sortOrder>
            <outputSelector>CategoryHistogram</outputSelector>
        </findItemsByCategoryRequest>
        """

        with Client(headers=headers) as client:
            response = client.post(url, data=payload)
        print(response.read())


    def search_items(self, q=None, gtin=None, charity_ids=None, fieldgroups=None, compatibility_filter=None, auto_correct=None,
                     category_ids=None, _filter=None, sort=None, limit=None, offset=None, aspect_filter=None, epid=None):

        params = {'q': q, 'gtin': gtin, 'charity_ids': charity_ids, 'fieldgroups': fieldgroups,
                  'compatibility_filter': compatibility_filter, 'auto_correct': auto_correct,
                  'category_ids': category_ids, 'filter': _filter, 'sort': sort, 'limit': limit,
                  'offset': offset, 'aspect_filter': aspect_filter, 'epid':epid}

        f_params_key = list(filter(lambda x: params[x] is not None, params))

        query = ''
        for i, key in enumerate(f_params_key):
            if i == 0:
                query = f'{key}={params[key]}'
            else:
                query += f'&{key}={params[key]}'

        endpoint = f'https://api.ebay.com/buy/browse/v1/item_summary/search?{query}'

        headers = {
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': f'Bearer {self.accessToken["access_token"]}',
            'Content-Type': 'application/json',
            'Content-Language': 'en-US,en;q=0.9',
            'X-EBAY-C-ENDUSERCTX': 'contextualLocation=country=US',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }

        with Client(headers=headers) as client:
            response = client.get(endpoint)

        if response != 200:
            response.raise_for_status()

        return response

    def get_item(self, item_id=None, fieldgroups=None):

        params = {'item_id': item_id, 'fieldgroups': fieldgroups}

        f_params_key = list(filter(lambda x: params[x] is not None, params))

        query = ''
        for i, key in enumerate(f_params_key):
            if i == 0:
                query = f'{params[key]}'
            else:
                query += f'&{key}={params[key]}'

        endpoint = f'https://api.ebay.com/buy/browse/v1/item/{query}'

        headers = {
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': f'Bearer {self.accessToken["access_token"]}',
            'Content-Type': 'application/json',
            'Content-Language': 'en-US,en;q=0.9',
            'X-EBAY-C-ENDUSERCTX': 'contextualLocation=country=US',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }

        with Client(headers=headers) as client:
            response = client.get(endpoint)

        if response != 200:
            response.raise_for_status()

        return response

if __name__ == '__main__':
    e = Core()
    e.getAccessToken()
    result = e.search_items(limit=200, category_ids=145944, sort='-price', offset=0)
    pretty_json = json.dumps(result.json(), indent=2)
    print(pretty_json)