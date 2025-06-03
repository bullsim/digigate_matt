class DigiGateCover(CoverEntity):
    def __init__(self, entry):
        self._name = "DigiGate"
        self.api_code = entry.data["api_code"]
        self.ip = entry.data["ip"]
        self.open_mode = entry.data.get("open_mode", "latch")
        self.duration = entry.data.get("duration", 3)

    @property
    def name(self):
        return self._name

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
        url = f"http://{self.ip}:8080/API"
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
