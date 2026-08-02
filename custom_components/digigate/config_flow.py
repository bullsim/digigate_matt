from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol


class DigiGateConfigFlow(config_entries.ConfigFlow, domain="digigate"):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="DigiGate", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip"): str,
                vol.Required("api_code"): str
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        # Must be a static method on the config flow class. It was previously a
        # module-level function in __init__.py, where Home Assistant never looks
        # for it, so the options were unreachable from the UI.
        from .options_flow import DigiGateOptionsFlowHandler
        return DigiGateOptionsFlowHandler(config_entry)
