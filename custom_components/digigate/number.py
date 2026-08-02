"""A hold-open duration the household can set from the dashboard.

The gate's own API takes a duration with its 'open' request and closes itself
when the timer expires. Exposing that as a number entity means the hold can be
changed without going into the integration's options.
"""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN

DEFAULT_HOLD_MINUTES = 5


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DigiGateHoldMinutes(hass, entry)])


class DigiGateHoldMinutes(NumberEntity, RestoreEntity):
    _attr_name = "DigiGate hold"
    _attr_native_min_value = 1
    _attr_native_max_value = 60
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "min"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:timer-outline"

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"digigate_hold_{entry.entry_id}"
        self._value = float(
            entry.options.get("hold_minutes", DEFAULT_HOLD_MINUTES)
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        # Survive restarts, so a chosen hold is not silently reset.
        last = await self.async_get_last_state()
        if last is not None and last.state not in (None, "unknown", "unavailable"):
            try:
                self._value = float(last.state)
            except ValueError:
                pass
        self._publish()

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value):
        self._value = float(value)
        self._publish()
        self.async_write_ha_state()

    def _publish(self):
        """Share the value with the cover entity via hass.data."""
        store = self.hass.data.setdefault(DOMAIN, {}).setdefault(self._entry_id, {})
        store["hold_minutes"] = self._value
