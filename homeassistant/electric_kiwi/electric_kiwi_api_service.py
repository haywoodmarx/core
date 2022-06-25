"""The Electric Kiwi Authorisation Implementation"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from datetime import timedelta, datetime
from hashlib import md5

from types import SimpleNamespace

from . import cryptoJS

import logging
import random
import json
import requests

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
)

from .const import (
    DOMAIN,
    CONF_AUTH_OBJ,
    CONF_CUST_OBJ
)

class ElectricKiwiException(Exception):
    def __init__(self, responseData):
        self.code: int = responseData["error"]["code"]
        self.title: str = responseData["error"]["title"]
        self.detail: str = responseData["error"]["detail"]

class ElectricKiwiRequireLoginException(ElectricKiwiException):
    pass

class AuthSession(object):
    token: str = None
    secret: str = None
    expiry: int = None
    secret_position: str = None

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def from_json(data) -> AuthSession:
        return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

class Customer(object):
    id: str = None
    sid: str = None
    expiry: int = None
    connectionId: str = None

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def from_json(data) -> Customer:
        return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

class ElectricKiwiAPIService(object):

    _hass: HomeAssistant = None
    _entry: ConfigEntry = None

    _customer: Customer = None
    _auth_session: AuthSession = None

    _email: str = None
    _password: str = None

    _LOGGER = logging.getLogger(__name__)

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._entry = entry
        self._hass = hass

        self._email = entry.data[CONF_USERNAME]
        self._password = entry.data[CONF_PASSWORD]

        self._customer = self._get_customer_from_storage()
        self._auth_session = self._get_auth_session_from_storage()

    def _get_auth_session_from_storage(self) -> AuthSession | None:
        authJson = self._entry.data.get(CONF_AUTH_OBJ)

        if authJson:
            self._LOGGER.debug("Retrieved saved Auth Session object: " + json.dumps(authJson))
            return AuthSession.from_json(authJson)
        else:
            self._LOGGER.debug("Couldn't retrieve an existing Auth Session Object. Creating a new one")
            return None

    def _update_auth_session_in_storage(self):
        authJson = self._auth_session.to_json()
        self._LOGGER.debug("Updating saved Auth Session object: " + json.dumps(authJson))

        self._hass.config_entries.async_update_entry(
            self._entry,
            data={
                **self._entry.data,
                CONF_AUTH_OBJ: authJson,
            },
        )

    def _get_customer_from_storage(self) -> Customer | None:
        customerJson = self._entry.data.get(CONF_CUST_OBJ)

        if customerJson:
            self._LOGGER.debug("Retrieved saved Customer object: " + json.dumps(customerJson))
            return Customer.from_json(customerJson)
        else:
            self._LOGGER.debug("Couldn't retrieve an existing Customer Object. Creating a new one")
            return None

    def _update_customer_in_storage(self):
        customerJson = self._customer.to_json()
        self._LOGGER.debug("Updating saved Customer object: " + json.dumps(customerJson))

        self._hass.config_entries.async_update_entry(
            self._entry,
            data={
                **self._entry.data,
                CONF_CUST_OBJ: customerJson,
            },
        )

    async def request(self, endpoint: str, params=None, type: str='GET') -> dict:
        authSession = await self.async_get_auth_session()
        customer = await self.async_get_customer()

        return await self._request(endpoint, authSession, customer, params, type)

    async def _async_generate_auth_session(self) -> AuthSession:
        data = await self._request('/at/')

        self._LOGGER.debug("Requested new at_token. Got response: " + json.dumps(data))

        authSession = AuthSession()
        authSession.secret = data['token'][2:-2]
        authSession.secret_position = int(data['token'][:2])
        authSession.token = data['token']
        authSession.expiry = (datetime.now() + timedelta(minutes=25)).timestamp()

        return authSession

    async def _async_generate_customer(self, auth: AuthSession, email: str, password: str, customer_index=0) -> Customer:
        payload = {
            'email'   : email,
            'password': self._password_hash(password),
        }

        data = await self._request('/login/', auth=auth, customer=None, params=payload, type='POST')

        customer = Customer()
        customer.id = data['customer'][customer_index]['id']
        customer.connectionId = data['customer'][customer_index]['connection']['id']
        customer.sid = data['sid']
        customer.expiry = (datetime.now() + timedelta(minutes=25)).timestamp()

        return customer

    async def async_get_auth_session(self) -> AuthSession:
        if (self._auth_session is None or
                self._auth_session.expiry is None or
                    self._auth_session.expiry < datetime.now().timestamp()):

            self._auth_session = await self._async_generate_auth_session()

            self._update_auth_session_in_storage()
            self._LOGGER.debug("Had " + ("no" if self._auth_session is None else "expired") + " auth session, so retrieved a new one")

        return self._auth_session

    async def async_get_customer(self) -> Customer:
        if (self._customer is None or
                self._customer.id is None or
                    self._customer.sid is None or
                        self._customer.connectionId is None or
                            self._customer.expiry < datetime.now().timestamp()):

            authSession = await self.async_get_auth_session()

            self._customer = await self._async_generate_customer(authSession, self._email, self._password)
            self._update_customer_in_storage()
            self._LOGGER.debug("Had no customer object so requested a new one")

        return self._customer

    async def _request(self, endpoint: str, auth: AuthSession=None, customer: Customer=None, params: dict={}, type: str='GET') -> dict:
        url = 'https://api.electrickiwi.co.nz{}'.format(endpoint)

        headers = {
            'x-client': 'ek-app',
            'x-apiversion': '1_1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; MI 5 Build/OPM7.181205.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.109 Mobile Safari/537.36',
            'X-Requested-With': 'nz.co.electrickiwi.mobile.app',
        }

        if auth and auth.secret and auth.secret_position:
            headers['x-token'] = self._get_endpoint_token(auth, endpoint)

        if customer and customer.sid:
            headers['x-sid'] = customer.sid

        data = await self._hass.async_add_executor_job(self._hassRequest, type, url, headers, params)

        if 'error' in data:
            raise ElectricKiwiException(data)

        return data['data']

    # Helper Methods

    def _get_endpoint_token(self, auth: AuthSession, endpoint: str) -> str:
        length = random.randint(10, len(auth.secret) - 2)
        secret = auth.secret[:length]

        thirtySecondsInFuture = (datetime.now() + timedelta(seconds=30)).timestamp()

        data = endpoint + '|' + str(int(thirtySecondsInFuture)) + '|' + ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        encrypted = cryptoJS.encrypt(data.encode(), secret.encode()).decode()

        return encrypted[:auth.secret_position] + str(length) + encrypted[auth.secret_position:]

    def _password_hash(self, password) -> str:
        return md5(password.encode('utf-8')).hexdigest()

    def _hassRequest(self, type, endpoint, headers, json) -> JSON:
        return requests.request(type, endpoint, headers=headers, json=json).json()