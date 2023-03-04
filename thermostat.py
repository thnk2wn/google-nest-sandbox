from enum import Enum
import atexit
import json

from credentials import get_credentials_installed
from googleapiclient.discovery import build
from urllib.error import HTTPError
from temperature import celsius_to_fahrenheit, fahrenheit_to_celsius

ThermostatMode = Enum('ThermostatMode', ['Cool', 'Heat'])

class Thermostat:
  def __init__(self, projectId, deviceName, debug):
    self.projectId = projectId
    self.projectParent = f"enterprises/{projectId}"
    self.deviceName = deviceName
    self.debug = debug
    credentials = get_credentials_installed()
    self.service = build(serviceName='smartdevicemanagement', version='v1', credentials=credentials)
    atexit.register(self.cleanup)

  def cleanup(self):
    self.service.close()
    print('Service closed')

  def __execute(self, request):
    try:
      response = request.execute()

      if self.debug:
        print(json.dumps(response, sort_keys=True, indent=4))

      return response

    except HTTPError as e:
      if self.debug:
        print('Error response status code : {0}, reason : {1}'.format(e.status_code, e.error_details))
      raise e

  def __get_device(self, response):
    device = None
    device_count = len(response['devices'])

    if (self.deviceName) is not None:
      full_device_name = f"{self.projectParent}/devices/{self.deviceName}"

      for d in response['devices']:
        if d['name'] == full_device_name:
          device = d
          break

      if device is None:
        raise Exception("Failed find device by name")

    else:
      if device_count == 1:
        device = response['devices'][0]
      else:
        raise Exception(f'Found ${device_count} devices, expected 1')

    return device

  def initialize(self):
    request = self.service.enterprises().devices().list(parent=self.projectParent)
    response = self.__execute(request)
    device = self.__get_device(response)

    traits = device['traits']
    self.deviceName = device['name']
    self.mode = traits['sdm.devices.traits.ThermostatMode']['mode']
    self.tempC = traits['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
    self.tempF = celsius_to_fahrenheit(self.tempC)

    setpointTrait = traits['sdm.devices.traits.ThermostatTemperatureSetpoint']
    key = f'{self.mode.lower()}Celsius'
    self.setpointC = setpointTrait[key]
    self.setpointF = celsius_to_fahrenheit(self.setpointC)

    print(f'Nest mode is {self.mode}, ' +
          f'temp is {round(self.tempF, 0)} °F, ' +
          f'setpoint is {round(self.setpointF, 0)} °F')

  def set_mode(self, mode: ThermostatMode):
    # https://developers.google.com/nest/device-access/traits/device/thermostat-mode
    data = {
      "command": "sdm.devices.commands.ThermostatMode.SetMode",
      "params": {
        "mode": mode.name.upper()
      }
    }

    request = self.service.enterprises().devices().executeCommand(name=self.deviceName, body=data)
    response = self.__execute(request)

    print(f'Nest set to mode {mode.name}')

  def set_temp(self, mode: ThermostatMode, tempF: float):
    # Ensure / change thermostat mode first
    self.set_mode(mode)

    tempC = fahrenheit_to_celsius(tempF)

    # https://googleapis.github.io/google-api-python-client/docs/dyn/smartdevicemanagement_v1.enterprises.devices.html#executeCommand
    data = {
      "command": f"sdm.devices.commands.ThermostatTemperatureSetpoint.Set{mode.name}",
      "params": {
        f"{mode.name}Celsius": tempC
      }
    }

    request = self.service.enterprises().devices().executeCommand(name=self.deviceName, body=data)
    response = self.__execute(request)

    print(f'Nest set to temp {round(tempF, 0)} °F ({round(tempC, 0)} °C) for mode {mode.name}')
