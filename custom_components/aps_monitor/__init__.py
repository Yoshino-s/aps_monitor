import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApsApiClient
from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN
from .entity import *

SCAN_INTERVAL = timedelta(seconds=12)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        raise ConfigEntryNotReady

    username = entry.data.get(CONF_USERNAME)
    assert isinstance(username, str)
    password = entry.data.get(CONF_PASSWORD)
    assert isinstance(password, str)

    session = async_get_clientsession(hass)
    client = ApsApiClient(username, password, session)

    r = await client.async_login()
    _LOGGER.info(f"Login result: {r}")

    coordinator = ApsDataUpdateCoordinator(hass, client=client, device_list=await client.async_get_meter_list())

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, "sensor")
            )
    return True


class ApsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""
    def __init__(
        self, hass: HomeAssistant, client: ApsApiClient, device_list: list
    ) -> None:
        """Initialize."""
        self.api = client
        self.device_list = [str(int(i['Meter']['MeterID'])) for i in device_list]
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await asyncio.gather(*[
                self.api.async_get_instant(meter_id) for meter_id in self.device_list
            ])
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    r = all(await asyncio.gather(*[hass.config_entries.async_forward_entry_unload(entry, "sensor")]))
    if r:
        del hass.data[DOMAIN][entry.entry_id]
    return r
    

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
