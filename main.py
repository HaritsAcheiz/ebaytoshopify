from eBayAPI import Core
import json
from dataclasses import dataclass
import pandas as pd

@dataclass
class eBay2shopify:

    def extract_items(self):
        e = Core()
        e.getAccessToken()
        price_filters = ['price:[170],priceCurrency:USD,conditionIds:{1000}', 'price:[..170],priceCurrency:USD,conditionIds:{1000}']
        items_exist = False
        for _filter in price_filters[0:1]:
            offset = 0
            has_next = True
            while has_next:
                response = e.search_items(limit=200, category_ids=145944, sort='-price', offset=offset,
                                          fieldgroups='MATCHING_ITEMS,EXTENDED', _filter=_filter)
                offset += 200
                # pretty_json = json.dumps(response.json(), indent=2)
                # print(pretty_json)
                data = response.json()
                try:
                    data['next']
                except:
                    has_next = False
                item_summaries = data['itemSummaries']
                for item in item_summaries:
                    print(item)
                    if items_exist:
                        temp_data = pd.DataFrame.from_dict(item, orient='index')
                        temp_data = temp_data.transpose()
                        items = pd.concat([items, temp_data], copy=True)
                    else:
                        items = pd.DataFrame.from_dict(item, orient='index')
                        items = items.transpose()
                        items_exist = True

        items.to_csv('result.csv', index=False)

if __name__ == '__main__':
    e = eBay2shopify()
    result = e.extract_items()

    # e = Core()
    # e.getAccessToken()

    # result = e.search_items(limit=200, category_ids=145944, sort='-price', offset=0, _filter='price:[150],priceCurrency:USD,conditionIds:{1000}')
    # pretty_json = json.dumps(result.json(), indent=2)
    # print(pretty_json)

    # result = e.get_item(item_id='v1|166348606997|0')
    # pretty_json = json.dumps(result.json(), indent=2)
    # print(pretty_json)