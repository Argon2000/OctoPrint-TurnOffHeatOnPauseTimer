# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import Events
from octoprint.util import ResettableTimer

class TurnOffHeatOnPauseTimerPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.EventHandlerPlugin
):
    def __init__(self):
        self.timer = None

    # ~~ StartupPlugin mixin
    def on_after_startup(self):
        self._logger.info("Turn off heat on pause timer plugin loaded!")

    # ~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return {
            "timer_time_in_seconds": 600,
            "shut_off_heatbed": True,
            "shut_off_hotend": True
        }
    
    # ~~ TemplatePlugin mixin
    def get_template_vars(self):
        return {"plugin_version": self._plugin_version}
    
    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    # ~~ EventHandlerPlugin mixin
    def on_event(self, event, payload):
        if event == Events.PRINT_PAUSED:
            time_in_seconds = self._settings.get_float(["timer_time_in_seconds"])
            self._logger.info("Turn off heat on pause timer started! Will stop after {}".format(time_in_seconds))
            self.timer = ResettableTimer(time_in_seconds, self.turn_off_heat)
            self.timer.start()

    def turn_off_heat(self):
        printer = self._printer
        self.timer = None
        if printer.is_paused():
            shut_off_heatbed = self._settings.get_float(["shut_off_heatbed"])
            shut_off_hotend = self._settings.get_float(["shut_off_hotend"])
            if printer.heatedBed and shut_off_heatbed:
                printer.set_temperature("bed", 0)
            if shut_off_hotend:
                for i in range(printer.extruder.count):
                    printer.set_temperature("tool{}".format(i), 0)

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return {
            "turn_off_heat_on_pause_timer": {
                "displayName": "Turn_off_heat_on_pause_timer Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "Argon2000",
                "repo": "OctoPrint-TurnOffHeatOnPauseTimer",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/Argon2000/OctoPrint-TurnOffHeatOnPauseTimer/archive/{target_version}.zip",
            }
        }

__plugin_name__ = "Turn off heat on pause timer"
__plugin_version__ = "0.0.1"
__plugin_description__ = "Enables setting a timer for how long after the printer is paused that it should turn off hotend and/or heatbed."
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = TurnOffHeatOnPauseTimerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }