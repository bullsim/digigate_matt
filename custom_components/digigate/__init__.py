DOMAIN = "digigate"

async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "cover")
    )
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_forward_entry_unload(entry, "cover")

async def async_get_options_flow(config_entry):
    from .options_flow import DigiGateOptionsFlowHandler
    return DigiGateOptionsFlowHandler(config_entry)