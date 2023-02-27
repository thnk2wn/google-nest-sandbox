from enum import Enum
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

    print(f'Nest mode is {self.mode}, temp is {self.tempF} °F, setpoint is {self.setpointF} °F')

  def set_temp(self, mode: ThermostatMode, tempF: float):
    tempC = fahrenheit_to_celsius(tempF)

    data = {
      "command": f"sdm.devices.commands.ThermostatTemperatureSetpoint.Set{mode.name}",
      "params": {
        f"{mode.name}Celsius": tempC
      }
    }

    #body = json.dumps(data)
    request = self.service.enterprises().devices().executeCommand(name=self.deviceName, body=data)
    response = self.__execute(request)

  # https://googleapis.github.io/google-api-python-client/docs/dyn/smartdevicemanagement_v1.enterprises.devices.html#executeCommand