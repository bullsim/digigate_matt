from homeassistant.components.cover import CoverEntity, CoverEntityFeature
import aiohttp

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DigiGateCover(entry)])

class DigiGateCover(CoverEntity):
    def __init__(self, entry):
        self._name = "DigiGate"
        self.api_code = entry.data["api_code"]
        self.ip = entry.data["ip"]
        self.duration = entry.data.get("duration", 15)  # Default to 15 seconds

    @property
    def name(self):
        return self._name

    @property
    def is_closed(self):
        return None  # State unknown → both buttons stay active

    @property
    def supported_features(self):
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

    async def async_open_cover(self, **kwargs):
        await self._send_command("latch", duration=str(self.duration))
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        await self._send_command("close")
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
