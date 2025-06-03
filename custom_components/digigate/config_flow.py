from homeassistant import config_entries
import voluptuous as vol

class DigiGateConfigFlow(config_entries.ConfigFlow, domain="digigate"):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="DigiGate", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip"): str,
                vol.Required("api_code"): str,
                vol.Optional("mode", default="latch"): vol.In(["latch", "timed"])
            })
        )