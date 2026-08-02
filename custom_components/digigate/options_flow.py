from homeassistant import config_entries
import voluptuous as vol

DEFAULT_DURATION = 3

class DigiGateOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        current = self.config_entry.options or self.config_entry.data

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("open_mode", default=current.get("open_mode", "latch")): vol.In(["latch", "timed"]),
                vol.Optional("duration", default=current.get("duration", DEFAULT_DURATION)): vol.All(int, vol.Range(min=1)),
            })
        )