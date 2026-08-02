from homeassistant.components.cover import CoverEntity, CoverEntityFeature
import aiohttp


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
    async_add_entities([DigiGateCover(entry)], update_before_add=True)

class DigiGateCover(CoverEntity):
    def __init__(self, entry):
        self._attr_name = "DigiGate"
        self._attr_unique_id = f"digigate_{entry.data['ip'].replace('.', '_')}"
        self.api_code = entry.data["api_code"]
        self.ip = entry.data["ip"]
        self._url = _build_url(self.ip)
        self.open_mode = entry.options.get("open_mode", entry.data.get("open_mode", "latch"))
        self.duration = entry.options.get("duration", entry.data.get("duration", 3))

    @property
    def is_closed(self):
        return None

    @property
    def supported_features(self):
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

    async def async_open_cover(self, **kwargs):
        if self.open_mode == "timed":
            await self._send_command("open", duration=str(self.duration))
        else:
            await self._send_command("latch", duration="0")
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        await self._send_command("close")
        self.async_write_ha_state()

    async def _send_command(self, request, duration=None):
        url = self._url
        payload = {"apiCode": self.api_code, "request": request}
        if duration is not None:
            payload["duration"] = duration
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to send command to DigiGate: {resp.status}")

    @property
    def device_class(self):
        return "gate"