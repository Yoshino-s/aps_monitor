"""BlueprintEntity class"""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION


class ApsRemainEntity(CoordinatorEntity, SensorEntity):
    _attr_device_class = "energy"
    _attr_native_unit_of_measurement = "kWh"
    _attr_state_class = "total"
    def __init__(self, coordinator, id: str):
        super().__init__(coordinator)
        self.id = id

    @property
    def native_value(self):
        return self.coordinator.data[self.id]["ekwh"]

    @property
    def unique_id(self) -> str | None:
        return "aps_remain_" + self.id
        

class ApsUsedEntity(CoordinatorEntity, SensorEntity):
    _attr_device_class = "energy"
    _attr_native_unit_of_measurement = "kWh"
    _attr_state_class = "total_increasing"
    def __init__(self, coordinator, id: str):
        super().__init__(coordinator)
        self.id = id

    @property
    def native_value(self):
        return self.coordinator.data[self.id]["tkwh"]

    @property
    def unique_id(self) -> str | None:
        return "aps_used_" + self.id

class ApsCurrentEntity(CoordinatorEntity, SensorEntity):
    _attr_device_class = "power"
    _attr_native_unit_of_measurement = "W"
    _attr_state_class = "measurement"
    def __init__(self, coordinator, id: str):
        super().__init__(coordinator)
        self.id = id

    @property
    def native_value(self):
        return self.coordinator.data[self.id]["power"]

    @property
    def unique_id(self) -> str | None:
        return "aps_current_" + self.id