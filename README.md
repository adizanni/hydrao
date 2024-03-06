
# Hydrao Shower Head

![image](https://github.com/adizanni/hydrao/assets/35622920/2507ed3b-d70c-4d1a-8aa7-7e14cd125f79)

This custom component for [Home Assistant](https://www.home-assistant.io) is supporting active monitoring of the [Hydrao](https://www.hydrao.com/en/) [shower head](https://www.hydrao.com/en/store/showerhead-aloe#/2-couleur-chrome) via BLE.

![image](https://github.com/adizanni/hydrao/assets/35622920/2b3d68ea-7744-4896-a967-de5910b785c9)

## Additional Info

The integration should work out of the box. In order to discover the hydrao device, you should activate it with running water until the integration is fully recognized by the config flow.
It works most of the times.

You will see the Average and Current Temperature of the water, the current and total volume of the consumed water (across all showers) and the duration of the shower.

The device is disconnecting by design, so the value of the sensors will be valid during a running shower, after the entities will become unavailable. You should persist the value of the sensors using input_numbers and automation to set the values (excluding unavailable states).

I only tested the integration with Aloe model and only having one at home (do not know what happens if you have more than 1).

I have also only tested the integration having the bluetooth adapter installed in the home assistant server (no bluetooth proxy). Of course, in this case, the home assistant server should not be far from the shower head.

The integration is very experimental so use it in a test environment and only when you feel confident move it to your prod environment.

I will soon integrate it with HACS.

I wanted to thank @kamaradclimber for the base work he did to reverse engineer the Hydrao data structures; you will find his work in [this](https://github.com/kamaradclimber/hydrao-dump) repository. Based on this work I'm also developing an mqtt integration to get rid of the dependency with howe assistant bluetooth adapter. Of course this means you have a Rasperry close to the shower

## ESPHome

For those of you who have not the home assistant bluetooth scanner close to the shower head, you can configure your Shower Head using BLE Client sensors, this way:

```yaml
ble_client:
  - mac_address: <MAC Address of the device>
    id: hydrao_aloe_1
```

and the sensors (you can adjust the id, name and update_interval to your need and capacity of the ESP device):

Total Volume:
```yaml
  - platform: ble_client
    type: characteristic
    ble_client_id: hydrao_aloe_1
    name: "Shower Total Volume"
    service_uuid: '180f'
    characteristic_uuid: 'ca1c'
    unit_of_measurement: 'L'
    device_class: 'water'
    update_interval: 2000ms
    lambda: |-
      if (x.size() >= 2) {
        uint16_t value = (x[1] << 8) | x[0];
        return static_cast<float>(value);
      }
      return NAN;
```
Current Volume:
```yaml
  - platform: ble_client
    type: characteristic
    ble_client_id: hydrao_aloe_1
    name: "Shower Current Volume"
    service_uuid: '180f'
    characteristic_uuid: 'ca1c'
    unit_of_measurement: 'L'
    device_class: 'water'
    update_interval: 2000ms
    lambda: |-
      if (x.size() >= 4) {
        uint16_t value = (x[3] << 8) | x[2];
        return static_cast<float>(value);
      }
      return NAN;
```
Average Temperature of the running shower: 
```yaml
  - platform: ble_client
    type: characteristic
    ble_client_id: hydrao_aloe_1
    name: "Shower Average Temperature"
    service_uuid: '180f'
    characteristic_uuid: 'ca32'
    unit_of_measurement: '°C'
    device_class: 'temperature'
    update_interval: 2000ms
    lambda: |-
      if (x.size() >= 2) {
        uint16_t value = (x[3] << 8) | x[2];
        return static_cast<float>(value)/2;
      }
      return NAN;
```
Current Temperature of the running shower:
```yaml
  - platform: ble_client
    type: characteristic
    ble_client_id: hydrao_aloe_1
    name: "Shower Current Temperature"
    service_uuid: '180f'
    characteristic_uuid: 'ca32'
    unit_of_measurement: '°C'
    device_class: 'temperature'
    update_interval: 2000ms
    lambda: |-
      if (x.size() >= 2) {
        uint16_t value = (x[1] << 8) | x[0];
        return static_cast<float>(value)/2;
      }
      return NAN;
```
Duration of the running shower:
```yaml
  - platform: ble_client
    type: characteristic
    ble_client_id: hydrao_aloe_1
    name: "Shower Current Duration"
    service_uuid: '180f'
    characteristic_uuid: 'ca26'
    unit_of_measurement: 's'
    device_class: 'duration'
    update_interval: 2000ms
    lambda: |-
      if (x.size() >= 2) {
        uint16_t value = (x[1] << 8) | x[0];
        return static_cast<float>(value)/50;
      }
      return NAN;
```
