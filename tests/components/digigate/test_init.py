from homeassistant.setup import async_setup_component

async def test_setup(hass):
    assert await async_setup_component(hass, "digigate", {}) is True