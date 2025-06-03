async def async_setup_entry(hass, entry):
    hass.data.setdefault("digigate", {})
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "cover")
    )
    return True
