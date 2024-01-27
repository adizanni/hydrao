# Hydrao Shower Head

This custom component for [Home Assistant](https://www.home-assistant.io) is supporting active monitoring of the [Hydrao](https://www.hydrao.com/en/) [shower head](https://www.hydrao.com/en/store/showerhead-aloe#/2-couleur-chrome) via BLE 

# Additional Info

The integration should work out of the box. In order to discover the hydrao device, you should activate it with running water until the integration is fully recognized by the config flow.
It works most of the times.

You will see the Average and Current Temperature of the water, the current and total volume of the consumed water (across all showers) and the duration of the shower.

The device is disconnecting by design, so the value of the sensors will be valid during a running shower, after the entities will become unavailable. You should persist the value of the sensors using input_numbers and automation to set the values (excluding unavailable states).

I only tested the integration with Aloe model and only having one at home (do not know what happens if you have more than 1).

I have also only tested the integration having the bluetooth adapter installed in the home assistant server (no bluetooth proxy). Of course, in this case, the home assistant server should not be far from the shower head.

The integration is very experimental so use it in a test environment and only when you feel confident move it to your prod environment.

I will soon integrate it with HACS.

I wanted to thank @kamaradclimber for the base work he did to reverse engineer the Hydrao data structures; you will find his work in [this](https://github.com/kamaradclimber/hydrao-dump) repository. Based on this work I'm also developing an mqtt integration to get rid of the dependency with howe assistant bluetooth adapter. Of course this means you have a Rasperry close to the shower