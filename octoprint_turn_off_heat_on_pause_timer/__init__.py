# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import Events
from octoprint.util import ResettableTimer
from octoprint.util import RepeatedTimer

class TurnOffHeatOnPauseTimerPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.EventHandlerPlugin
):
    def __init__(self):
        self.stop_timer = None
        self.start_timer = None
        self.printer_profile = None
        self.last_temps = None
        self.paused_by_plugin = False

    # ~~ StartupPlugin mixin
    def on_after_startup(self):
        self._logger.debug("Turn off heat on pause timer plugin loaded!")

    # ~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return {
            "timer_time_in_seconds": 600,
            "shut_off_heatbed": True,
            "shut_off_hotend": True,
            "shut_off_heated_chamber": False,
            "restore_temperatures": False
        }
    
    # ~~ TemplatePlugin mixin
    def get_template_vars(self):
        return {"plugin_version": self._plugin_version}
    
    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]
    
    # ~~ AssetPlugin mixin
    def get_assets(self):
        return {
            "css": ["css/turn_off_heat_on_pause_timer.css"]
        }

    # ~~ EventHandlerPlugin mixin
    def on_event(self, event, payload):
        if event == Events.PRINT_RESUMED and self.last_temps != None and self.restore_temperatures:
            restore_temperatures = self._settings.get_boolean(["restore_temperatures"])
            if restore_temperatures:
                for k in self.last_temps.keys():
                    self._printer.set_temperature(k, self.last_temps[k])
                if self.stop_timer != None:
                    self.stop_timer.cancel()
                if self.check_temps_valid() == False:
                    self._logger.debug("Turn off heat on pause timer: Restoring temperatures, pausing and then resuming")
                    self.start_timer = RepeatedTimer(1, self.start_on_temperatures_restored)
                    self.start_timer.start()
                    self.paused_by_plugin = True
                    self._printer.pause_print()
        if event == Events.PRINT_PAUSED:
            if self.paused_by_plugin:
                self.paused_by_plugin = False
                return
            self.last_temps = dict()
            temps = self._printer.get_current_temperatures()
            shut_off_heatbed = self._settings.get_boolean(["shut_off_heatbed"])
            shut_off_hotend = self._settings.get_boolean(["shut_off_hotend"])
            shut_off_heated_chamber = self._settings.get_boolean(["shut_off_heated_chamber"])
            for k in temps.keys():
                if ("tool" in k) and shut_off_hotend:
                    self.last_temps[k] = temps[k]["target"]
                if k == "bed" and shut_off_heatbed:
                    self.last_temps[k] = temps[k]["target"]
                if k == "chamber" and shut_off_heated_chamber:
                    self.last_temps[k] = temps[k]["target"]
            time_in_seconds = self._settings.get_float(["timer_time_in_seconds"])
            self._logger.debug("Turn off heat on pause timer started! Will stop after {} seconds".format(time_in_seconds))
            self.stop_timer = ResettableTimer(time_in_seconds, self.turn_off_heat)
            self.stop_timer.start()

    def turn_off_heat(self):
        printer = self._printer
        self.stop_timer = None
        if printer.is_paused():
            shut_off_heatbed = self._settings.get_boolean(["shut_off_heatbed"])
            shut_off_hotend = self._settings.get_boolean(["shut_off_hotend"])
            shut_off_heated_chamber = self._settings.get_boolean(["shut_off_heated_chamber"])
            for k in self._printer.get_current_temperatures().keys():
                if ("tool" in k) and shut_off_hotend:
                    self._logger.debug("Turn off heat on pause timer: Turning off hotend {}".format(k))
                    self._printer.set_temperature(k, 0)
                if k == "bed" and shut_off_heatbed:
                    self._logger.debug("Turn off heat on pause timer: Turning off heatbed")
                    self._printer.set_temperature(k, 0)
                if k == "chamber" and shut_off_heated_chamber:
                    self._logger.debug("Turn off heat on pause timer: Turning off heated chamber")
                    self._printer.set_temperature(k, 0)

    def start_on_temperatures_restored(self):
        printer = self._printer
        if printer.is_paused() and self.check_temps_valid():
            self.last_temps = None
            self.start_timer.cancel()
            self.start_timer = None
            printer.resume_print()

    def check_temps_valid(self):
        temps_valid = True
        if self.last_temps != None:
            current_temps = self._printer.get_current_temperatures()
            for k in current_temps.keys():
                if k in self.last_temps.keys():
                    current = current_temps[k]["actual"]
                    target = self.last_temps[k]
                    if current < target:
                        temps_valid = False
                        break
        return temps_valid

    # ~~ Softwareupdate hook
    def get_update_information(self):
        return {
            "turn_off_heat_on_pause_timer": {
                "displayName": "Turn off heat on pause timer",
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
__plugin_description__ = "Enables setting a timer for how long after the printer is paused that it should turn off hotend, heatbed and/or chamber."
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = TurnOffHeatOnPauseTimerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
