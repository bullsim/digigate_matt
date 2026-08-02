"""Lock-open switch.

The API has two ways to open:

  latch  - opens with no timer; the gate stays open until told to close
  open   - opens for a duration, then the gate closes itself

The cover entity uses the timed form. This switch exposes the latch, which is
what "hold it open" means in practice - deliveries, guests arriving, moving
things in and out.
"""

from homeassistant.components.switch import SwitchEntity

from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DigiGateLockOpen(hass, entry)])


class DigiGateLockOpen(SwitchEntity):
    _attr_name = "DigiGate locked open"
    _attr_icon = "mdi:gate-open"

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"digigate_lockopen_{entry.entry_id}"
        self._on = False

    @property
    def is_on(self):
        return self._on

    def _cover(self):
        """The cover entity owns the HTTP client; reuse it rather than duplicate."""
        return self.hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get("cover")

    async def async_turn_on(self, **kwargs):
        cover = self._cover()
        if cover is None:
            return
        # duration 0 means no timer: stay open until closed.
        if await cover.send_command("latch", duration="0") is not None:
            self._on = True
            await cover.async_update()
            cover.async_write_ha_state()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        cover = self._cover()
        if cover is None:
            return
        if await cover.send_command("close") is not None:
            self._on = False
            await cover.async_update()
            cover.async_write_ha_state()
        self.async_write_ha_state()

    async def async_update(self):
        """Fall back to closed if the gate reports itself shut."""
        cover = self._cover()
        if cover is not None and cover.is_closed:
            self._on = False
