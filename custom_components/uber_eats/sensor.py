"""Uber Eats sensors"""
import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.const import CONF_NAME
from .api import UberEatsApi

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, config_entry, async_add_entities):
    sid = config_entry.data.get("sid")
    user_uuid = config_entry.data.get("user_uuid")
    country_code = config_entry.data.get("country_code")
    timezone = config_entry.data.get("timezone")

    api = UberEatsApi(sid, user_uuid, country_code, timezone)

    async def async_update_data():
        return api.get_deliveries()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Uber Eats Orders",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([UberEatsSensor(coordinator)])

class UberEatsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Uber Eats Active Orders"

    @property
    def state(self):
        data = self.coordinator.data
        if data and "data" in data and "orders" in data["data"]:
            return len(data["data"]["orders"])
        return 0

    @property
    def extra_state_attributes(self):
        return self.coordinator.data.get("data", {})
