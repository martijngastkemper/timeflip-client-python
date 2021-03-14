from datetime import date
from functools import cached_property
import requests


class Productive:
    base_url = 'https://api.productive.io/api/v2/'

    def __init__(self, api_token, organization_id):
        self.headers = {
            'Content-Type': 'application/vnd.api+json',
            'X-Auth-Token': api_token,
            'X-Organization-Id': organization_id,
        }
        self.today = '2021-03-10'

    def time_entries(self):
        r = requests.get(
            "{0}time_entries?filter[person_id]={1}&filter[before]={2}&filter[after]={2}".format(self.base_url,
                                                                                       self.person_id, self.now),
            headers=self.headers)

        data = r.json().get("data")
        included = r.json().get("included")
        time_entries = []

        for time_entry in data:
            time_entries.append(self.time_entry_to_str(time_entry, data, included))

        return time_entries

    def time_entry_to_str(self, time_entry, data, included):
        service_id = time_entry['relationships']['service']
        service = self.get_included(service_id, included)

        deal_id = service['relationships']['deal']
        deal = self.get_included(deal_id, included)

        return {
            "id": time_entry['id'],
            "description": "{0} - {1}".format(deal['attributes']['name'], service['attributes']['name'])
        }

    def start_time_entry(self, id) -> bool:
        r = requests.patch("{0}time_entries/{1}/start".format(self.base_url, id), headers=self.headers)
        return r.status_code == requests.codes.ok

    def get_included(self, relationship, included):
        for include in included:
            if include['id'] == relationship['data']['id'] and include['type'] == relationship['data']['type']:
                return include

    @cached_property
    def person_id(self):
        print(self.headers)
        r = requests.get("{0}organization_memberships".format(self.base_url), headers=self.headers)
        return r.json().get('data')[0]['relationships']['person']['data']['id']

    @cached_property
    def now(self):
        return date.today().strftime("%Y-%m-%d")

# api = Productive()
#
# print(api.time_entries())
# print(api.time_entries())
#
# api.start_time_entry('6336597')
