DOMAIN = "digigate"
PLATFORMS = ["cover", "number"]


async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    # async_forward_entry_setup (singular) was removed from Home Assistant and
    # raises AttributeError. The plural form is also awaited rather than fired
    # as a background task, so a failure surfaces as a setup error instead of a
    # silently missing entity.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass, entry):
    """Reload when options change, so open_mode and duration take effect."""
    await hass.config_entries.async_reload(entry.entry_id)
