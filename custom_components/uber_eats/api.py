"""Uber Eats API"""
import logging
from datetime import datetime
import requests

_LOGGER = logging.getLogger(__name__)

class UberEatsApi:
    def __init__(self, sid, user_uuid, locale_code, timezone):
        self._sid = sid
        self._user_uuid = user_uuid
        self._locale_code = locale_code
        self._timezone = timezone
        self._url_base = f'https://www.ubereats.com/api/getActiveOrdersV1?localeCode={self._locale_code}'

    def get_deliveries(self):
        headers = {
            "Content-Type": "application/json",
            "X-CSRF-Token": "x",
            "Cookie": f"sid={self._sid};_userUuid={self._user_uuid};"
        }
        data = {
            "orderUuid": None,
            "timezone": self._timezone,
            "showAppUpsellIllustration": True
        }
        try:
            response = requests.post(self._url_base, headers=headers, json=data)
            if response.status_code == requests.codes.ok:
                return response.json()
            else:
                _LOGGER.error(f"Error fetching orders: {response.status_code} - {response.text}")
        except Exception as e:
            _LOGGER.exception("Exception while fetching Uber Eats data: %s", e)
        return {}

    def check_auth(self):
        headers = {
            "Content-Type": "application/json",
            "X-CSRF-Token": "x",
            "Cookie": f"sid={self._sid};_userUuid={self._user_uuid};"
        }
        data = {
            "orderUuid": None,
            "timezone": self._timezone,
            "showAppUpsellIllustration": False
        }
        try:
            response = requests.post(self._url_base, headers=headers, json=data)
            return response.status_code == 200 and response.json().get("status") !="ok"
        except Exception as e:
            _LOGGER.warning("Auth check failed: %s", e)
            return False

