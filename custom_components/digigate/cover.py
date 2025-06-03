from homeassistant.components.cover import CoverEntity
from homeassistant.const import STATE_OPEN, STATE_CLOSED
import aiohttp

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DigiGateCover(entry)])

class DigiGateCover(CoverEntity):
    def __init__(self, entry):
        self._name = "DigiGate"
        self._state = STATE_CLOSED
        self.api_code = entry.data["api_code"]
        self.ip = entry.data["ip"]
        self.mode = entry.data.get("mode", "latch")

    @property
    def name(self):
        return self._name

    @property
    def is_closed(self):
        return self._state == STATE_CLOSED

    async def async_open_cover(self, **kwargs):
        if self.mode == "timed":
            await self._send_command("open", duration="300")
        else:
            await self._send_command("latch", duration="0")
        self._state = STATE_OPEN
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        await self._send_command("close")
        self._state = STATE_CLOSED
        self.async_write_ha_state()

    async def _send_command(self, request, duration=None):
        url = f"http://{self.ip}:8080/API"
        payload = {"apiCode": self.api_code, "request": request}
        if duration:
            payload["duration"] = duration
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to send command to DigiGate: {resp.status}")

    @property
    def device_class(self):
        return "gate"