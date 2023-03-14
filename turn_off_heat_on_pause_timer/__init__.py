import octoprint.plugin
from octoprint.events import Events
from octoprint.util import ResettableTimer

class TurnOffHeatOnPauseTimerPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
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

__plugin_name__ = "Turn off heat on pause timer"
__plugin_version__ = "0.0.1"
__plugin_description__ = "Enables setting a timer for how long after the printer is paused that it should turn off hotend and/or heatbed."
__plugin_pythoncompat__ = ">=3.7,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = TurnOffHeatOnPauseTimerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {}