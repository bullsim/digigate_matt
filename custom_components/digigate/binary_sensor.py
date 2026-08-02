"""Connectivity sensor.

The API exposes no health or firmware endpoint - only latch, open, close and
status - so "healthy" here means exactly one thing: the unit answered its last
status poll. That is honest and useful; anything more would be invented.
"""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DigiGateOnline(hass, entry)])


class DigiGateOnline(BinarySensorEntity):
    _attr_name = "DigiGate online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = None

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"digigate_online_{entry.entry_id}"

    @property
    def is_on(self):
        cover = self.hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get("cover")
        if cover is None:
            return None
        return bool(getattr(cover, "_attr_available", True))

    @property
    def extra_state_attributes(self):
        cover = self.hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get("cover")
        if cover is None:
            return {}
        return {"endpoint": getattr(cover, "_url", None)}
