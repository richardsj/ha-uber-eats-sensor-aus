import pytz
import pycountry
import voluptuous as vol
from datetime import datetime
from homeassistant import config_entries

DOMAIN = "uber_eats"


def get_matching_country_codes(timezone_name):
    try:
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        offset = now.utcoffset()

        matching_codes = set()
        for code, timezones in pytz.country_timezones.items():
            for zone in timezones:
                if datetime.now(pytz.timezone(zone)).utcoffset() == offset:
                    matching_codes.add(code)
                    break
        return sorted(matching_codes)
    except Exception:
        return []


def code_to_name_dict(code_list):
    return {
        code: pycountry.countries.get(alpha_2=code).name
        for code in code_list
        if pycountry.countries.get(alpha_2=code)
    }


class UberEatsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            country_code = user_input.get("country_code_override") or user_input.get("country_code_select")
            return self.async_create_entry(title="Uber Eats", data={
                "country_code": country_code,
                "timezone": user_input["timezone"],
                "sid": user_input["sid"],
                "user_uuid": user_input["user_uuid"]
            })

        timezone = self.hass.config.time_zone or "UTC"
        matching_codes = get_matching_country_codes(timezone)
        country_dict = code_to_name_dict(matching_codes)

        schema = vol.Schema({
            vol.Required("timezone", default=timezone): str,
            vol.Optional("country_code_select"): vol.In(country_dict),
            vol.Optional("country_code_override"): str,
            vol.Required("sid"): str,
            vol.Required("user_uuid"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "note": "You can override the dropdown with a custom ISO 3166-1 alpha-2 country code."
            }
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return UberEatsOptionsFlowHandler(config_entry)


class UberEatsOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("timezone", default=self.config_entry.options.get("timezone", "UTC")): str,
                vol.Optional("country_code_override", default=self.config_entry.options.get("country_code_override", "")): str,
                vol.Optional("country_code_select", default=self.config_entry.options.get("country_code_select", "")): str,
                vol.Required("sid", default=self.config_entry.options.get("sid", "")): str,
                vol.Required("user_uuid", default=self.config_entry.options.get("user_uuid", "")): str,
            })
        )

