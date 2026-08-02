import logging

import aiohttp

from homeassistant.components.cover import CoverEntity, CoverEntityFeature

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _build_url(host: str) -> str:
    """Accept a bare IP, a hostname, or a full URL.

    A bare IP or hostname keeps the original local behaviour
    (http://<host>:8080/API). A value that already looks like a URL is used as
    given, which allows the external https://<code>.digigate.me endpoint when
    Home Assistant cannot route to the unit's LAN address.
    """
    host = host.strip().rstrip("/")
    if host.startswith(("http://", "https://")):
        return host if host.endswith("/API") else f"{host}/API"
    return f"http://{host}:8080/API"


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DigiGateCover(hass, entry)], update_before_add=True)


class DigiGateCover(CoverEntity):
    _attr_should_poll = True

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._attr_name = "DigiGate"
        self._attr_unique_id = f"digigate_{entry.data['ip'].replace('.', '_')}"
        self.api_code = entry.data["api_code"]
        self.ip = entry.data["ip"]
        self._url = _build_url(self.ip)
        self.open_mode = entry.options.get("open_mode", entry.data.get("open_mode", "latch"))
        self.duration = entry.options.get("duration", entry.data.get("duration", 3))
        self._is_closed = None
        self._time_left = None

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def supported_features(self):
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

    @property
    def device_class(self):
        return "gate"

    @property
    def extra_state_attributes(self):
        return {"time_left": self._time_left} if self._time_left is not None else {}

    async def async_update(self):
        """The API supports a 'status' request the original never used.

        It returns {"status": "closed"|"open", "time_left": "<seconds>"}, which
        is enough for real state rather than a write-only button.
        """
        data = await self._send_command("status")
        if not data:
            return
        status = data.get("status")
        if status is not None:
            self._is_closed = status == "closed"
        self._time_left = data.get("time_left")

    @property
    def _hold_minutes(self):
        """Value of the DigiGate hold number entity, if it exists."""
        store = self.hass.data.get(DOMAIN, {}).get(self._entry_id, {})
        return store.get("hold_minutes")

    async def async_open_cover(self, **kwargs):
        """Open, holding for the configured time before the gate closes itself.

        The hold number entity wins when present, so the duration can be changed
        from the dashboard rather than in the integration options.
        """
        hold = self._hold_minutes
        if hold is not None:
            await self._send_command("open", duration=str(int(hold)))
        elif self.open_mode == "timed":
            await self._send_command("open", duration=str(self.duration))
        else:
            await self._send_command("latch", duration="0")
        await self.async_update()
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        await self._send_command("close")
        await self.async_update()
        self.async_write_ha_state()

    async def _send_command(self, request, duration=None):
        payload = {"apiCode": self.api_code, "request": request}
        if duration is not None:
            payload["duration"] = duration
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self._url, json=payload) as resp:
                    if resp.status != 200:
                        _LOGGER.error(
                            "DigiGate returned HTTP %s for '%s'", resp.status, request
                        )
                        self._attr_available = False
                        return None
                    data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            # Routing or DNS is by far the most likely cause, so name it rather
            # than leaving a bare connection error in the log.
            _LOGGER.error("Cannot reach DigiGate at %s: %s", self._url, err)
            self._attr_available = False
            return None

        self._attr_available = True
        if not data.get("success", True):
            _LOGGER.error(
                "DigiGate rejected '%s': %s", request, data.get("response_description")
            )
            return None
        return data
