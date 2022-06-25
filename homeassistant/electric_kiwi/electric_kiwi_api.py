"""The Electric Kiwi API Implementation"""

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .electric_kiwi_api_service import ElectricKiwiAPIService

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from hashlib import md5

from typing import List, Dict

from . import cryptoJS

import pdb
import logging
import asyncio
import random
import time
import json
import time
import datetime


class ElectricKiwiHopHelper:
    _hop_to_interval_map: Dict[str, int] = None

    def __init__(self):
        output = defaultdict(set)

        def index_to_hop(index: int) -> int:
            return str(timedelta(minutes=30*index))[:-3]

        peak_hours = [index_to_hop(x) for x in range(13, 18)] + [index_to_hop(x) for x in range(33, 42)]
        all_hours_list = [index_to_hop(x) for x in range(0, 47)]

        for index, time_stamp in enumerate(all_hours_list):
            if time_stamp not in peak_hours:
                output[str(time_stamp)] = index + 1

        self._hop_to_interval_map = output

    @property
    def all_hop(self) -> list[str]:
        return list(self._hop_to_interval_map.keys())

    @property
    def all_intervals(self) -> list[int]:
        return list(self._hop_to_interval_map.values())

    def hop_to_interval(self, hop: str) -> int:
        return self._hop_to_interval_map[hop]

    def interval_to_hop(self, interval: int) -> str:
        intervalIndex = self.all_intervals.index(interval)

        return self.all_hop[intervalIndex]

class ElectricKiwiAPI(object):

    _last_retrieved_hop: str = None
    _last_average_hop_utilisation: float = None

    _hopHelper = ElectricKiwiHopHelper()

    _LOGGER = logging.getLogger(__name__)

    @property
    def all_hop(self) -> list[str]:
        return self._hopHelper.all_hop

    @property
    def last_retrieved_hop(self):
        return self._last_retrieved_hop

    @property
    def last_average_hop_utilisation(self):
        return self._last_average_hop_utilisation

    def __init__(self, authHelper: ElectricKiwiAPIService):
        self._LOGGER.debug("Initialising new " + __name__)
        self._authHelper = authHelper

    async def get_average_hop_utilisation_for_last(self, daysCount: int):
        customer = await self._authHelper.async_get_customer()

        yesterday = datetime.datetime.now() - timedelta(days = 1)
        start_date = datetime.datetime.now() - timedelta(days = daysCount)

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = yesterday.strftime("%Y-%m-%d")

        url = '/consumption/averages/{customer_id}/{connection_id}/?start_date={start_date}&end_date={end_date}&group_by=day'.format(customer_id=customer.id, connection_id=customer.connectionId, start_date=start_date_str, end_date=end_date_str)

        data = await self._authHelper.request(url)

        total = sum(float(item['percent_consumption_adjustment']) for item in data['usage'].values())
        average = total / daysCount

        self._last_average_hop_utilisation = average

        return average

    async def get_last_hop_usage(self):
        customer = await self._authHelper.async_get_customer()
        two_days = date.timedelta(days = 2)
        inquiryDate = datetime.datetime.now() - two_days
        start_date = inquiryDate.strftime("%Y-%m-%d")
        end_date = inquiryDate.strftime("%Y-%m-%d")

        url = '/consumption/averages/{customer_id}/{connection_id}/?start_date={start_date}&end_date={end_date}&group_by=day'.format(customer_id=customer.id, connection_id=customer.connectionId, start_date=start_date, end_date=end_date)

        data = await self._authHelper.request(url)

        return data['usage'][start_date.strftime("%Y-%m-%d")]['percent_consumption_adjustment']

    async def running_balance(self):
        customer = await self._authHelper.async_get_customer()

        url = '/connection/details/{customer_id}/{connection_id}/'.format(customer_id=customer.id, connection_id=customer.connectId)

        data = await self._authHelper.request('/account/running_balance/{customer_id}/'.format(customer_id=self._customer['id']))

        return data

    async def connection_details(self):
        customer = await self._authHelper.async_get_customer()

        url = '/connection/details/{customer_id}/{connection_id}/'.format(customer_id=customer.id, connection_id=customer.connectionId)

        data = await self._authHelper.request('/connection/details/{customer_id}/{connection_id}/'.format(customer_id=self._customer['id'], connection_id=self._customer['connection']['id']))

        return data

    async def async_get_hop_hour(self) -> str:
        customer = await self._authHelper.async_get_customer()

        url = '/hop/{customer_id}/{connection_id}/'.format(customer_id=customer.id, connection_id=customer.connectionId)

        data = await self._authHelper.request(url)

        retrievedInterval = int(data['start']['interval'])
        retrievedHop: str = self._hopHelper.interval_to_hop(retrievedInterval)

        self._last_retrieved_hop = retrievedHop

        self._LOGGER.debug('Fetched current hour of power as: ' + retrievedHop + ' (Interval: ' + str(retrievedInterval) + ')')

        return retrievedHop

    async def async_set_hop_hour(self, hop: str) -> None:
        interval = self._hopHelper.hop_to_interval(hop)
        customer = await self._authHelper.async_get_customer()

        self._LOGGER.info('Setting hour of power to: ' + hop + ' (Interval: ' + str(interval) + ')')

        await self._authHelper.request('/hop/{customer_id}/{connection_id}/'.format(customer_id=customer.id, connection_id=customer.connectionId), params={'start': interval}, type='POST')

