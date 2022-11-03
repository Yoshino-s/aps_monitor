import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .entity import *

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for dev_id in coordinator.device_list:
        entities += [ApsRemainEntity(coordinator, dev_id), ApsUsedEntity(coordinator, dev_id), ApsCurrentEntity(coordinator, dev_id)]

    await async_add_entities(entities)

    hass.data[DOMAIN][f"{entry.entry_id}_devices"] = entities
