from datetime import date
from functools import cached_property
from typing import Union
import requests


def get_included(relationship, included) -> dict:
    for include in included:
        if include['id'] == relationship['data']['id'] and include['type'] == relationship['data']['type']:
            return include


class TimeEntry:

    def __init__(self, identifier: int, description: str):
        self.identifier = identifier
        self.description = description

    @staticmethod
    def create_from_json_api(json_api_time_entry: dict, json_api_included: dict):
        service_id = json_api_time_entry['relationships']['service']
        service = get_included(service_id, json_api_included)

        deal_id = service['relationships']['deal']
        deal = get_included(deal_id, json_api_included)

        return TimeEntry(json_api_time_entry['id'],
                         "{0} - {1}".format(deal['attributes']['name'], service['attributes']['name']).strip())


class Productive:
    base_url = 'https://api.productive.io/api/v2/'

    def __init__(self, api_token, organization_id):
        self.headers = {
            'Content-Type': 'application/vnd.api+json',
            'X-Auth-Token': api_token,
            'X-Organization-Id': organization_id,
        }

    def time_entries(self) -> list[TimeEntry]:
        r = requests.get(
            "{0}time_entries?filter[person_id]={1}&filter[before]={2}&filter[after]={2}".format(self.base_url,
                                                                                                self.person_id,
                                                                                                self.today),
            headers=self.headers)

        data = r.json().get("data")
        included = r.json().get("included")
        time_entries = []

        for time_entry in data:
            time_entries.append(TimeEntry.create_from_json_api(time_entry, included))

        return time_entries

    def started_time_entry(self) -> Union[TimeEntry, None]:
        r = requests.get(
            "{0}time_entries?filter[person_id]={1}&filter[before]={2}&filter[after]={2}".format(self.base_url,
                                                                                                self.person_id,
                                                                                                self.today),
            headers=self.headers)

        for time_entry in r.json().get('data'):
            if time_entry['attributes']['timer_started_at'] is not None:
                return TimeEntry.create_from_json_api(time_entry, r.json().get('included'))

    def start_time_entry(self, time_entry: TimeEntry) -> bool:
        r = requests.patch("{0}time_entries/{1}/start".format(self.base_url, time_entry.identifier), headers=self.headers)
        return r.status_code == requests.codes.ok

    def stop_time_entry(self) -> Union[TimeEntry, None]:
        started_time_entry = self.started_time_entry()

        if started_time_entry is None:
            return None

        requests.patch("{0}time_entries/{1}/stop".format(self.base_url, started_time_entry.identifier),
                       headers=self.headers)
        return started_time_entry

    @cached_property
    def person_id(self) -> int:
        r = requests.get("{0}organization_memberships".format(self.base_url), headers=self.headers)
        return r.json().get('data')[0]['relationships']['person']['data']['id']

    @cached_property
    def today(self) -> str:
        return date.today().strftime("%Y-%m-%d")
