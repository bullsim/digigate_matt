from homeassistant import config_entries
import voluptuous as vol

DEFAULT_DURATION = 15

class DigiGateConfigFlow(config_entries.ConfigFlow, domain="digigate"):
    async def async_step_user(self, user_input=None):
        """Step 1: Choose mode"""
        if user_input is not None:
            self.mode = user_input["open_mode"]
            return await self.async_step_config()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("open_mode", default="latch"): vol.In(["latch", "timed"])
            })
        )

    async def async_step_config(self, user_input=None):
        """Step 2: Enter config based on mode"""
        fields = {
            vol.Required("ip"): str,
            vol.Required("api_code"): str,
        }

        if self.mode == "timed":
            fields[vol.Required("duration", default=DEFAULT_DURATION)] = vol.All(int, vol.Range(min=1))

        if user_input is not None:
            # Save mode from first step into final data
            user_input["open_mode"] = self.mode
            return self.async_create_entry(title="DigiGate", data=user_input)

        return self.async_show_form(
            step_id="config",
            data_schema=vol.Schema(fields)
        )
