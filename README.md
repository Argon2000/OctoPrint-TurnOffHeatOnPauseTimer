# OctoPrint-TurnOffHeatOnPauseTimer

A plugin for OctoPrint that shuts off hotend, hotbed and/or chamber after a set amount of seconds following a pause.
Useful when just pausing to switch filament, and don't want the printer to cool down. Or when an AI (like Gadget) automatically pauses and you want to either resume shortly thereafter (no waiting for things to heat up), or shut down since you can't attend to the 3d-printer at the moment.

It can also be used to restore temperatures when later resuming, but I recommend using a GCODE script instead for that, since the plugin needs to pause the print again, heat up and then resume. Can possibly also cause issues with other plugins listening for a pause event.

Example Octoprint "Before print job is resumed" GCODE to restore temperatures:

```
; Restore all hotend temperatures, or shut down if value not present
{% for tool in range(printer_profile.extruder.count) %}
    {% if pause_temperature[tool] and pause_temperature[tool]['target'] is not none %}
        {% if tool == 0 and printer_profile.extruder.count == 1 %}
            M104 T{{ tool }} S{{ pause_temperature[tool]['target'] }}
        {% else %}
            M104 S{{ pause_temperature[tool]['target'] }}
        {% endif %}
    {% else %}
        {% if tool == 0 and printer_profile.extruder.count == 1 %}
            M104 T{{ tool }} S0
        {% else %}
            M104 S0
        {% endif %}
    {% endif %}
{% endfor %}

; Restore hotbed temperature, or shut down if value not present
{% if printer_profile.heatedBed %}
    {% if pause_temperature['b'] and pause_temperature['b']['target'] is not none %}
        M140 S{{ pause_temperature['b']['target'] }}
    {% else %}
        M140 S0
    {% endif %}
{% endif %}

; Wait for hotends to reach target temperatures
{% for tool in range(printer_profile.extruder.count) %}
    {% if pause_temperature[tool] and pause_temperature[tool]['target'] is not none %}
        {% if tool == 0 and printer_profile.extruder.count == 1 %}
            M109 T{{ tool }} S{{ pause_temperature[tool]['target'] }}
        {% else %}
            M109 S{{ pause_temperature[tool]['target'] }}
        {% endif %}
    {% endif %}
{% endfor %}

; Wait for hotbed to reach target temperature
{% if printer_profile.heatedBed %}
    {% if pause_temperature['b'] and pause_temperature['b']['target'] is not none %}
        M190 S{{ pause_temperature['b']['target'] }}
    {% endif %}
{% endif %}
```

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/Argon2000/OctoPrint-TurnOffHeatOnPauseTimer/archive/master.zip

# Configuration
## Timer (in seconds)
Set to desired time after the printer has paused that hotends/heatbed/chamber should turn off

Default: 600 (10 minutes)
## Turn off hotend
Wether or not hotend(s) should turn off

Default: ON (Will shut off hotend(s))
## Turn off heatbed
Wether or not heatbed should turn off

Default: ON (Will shut off heatbed)
## Turn off chamber
Wether or not chamber should turn off (If set to true and no chamber is present, this results in a error pop-up)

Default: OFF (Will NOT shut off chamber)

## Restore temperatures on resume (Better to use GCODE script)
If this plugin should handle restoring temperatures when a print resumes.

Default: OFF (Will NOT handle restoring temperatures)