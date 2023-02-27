
from thermostat import Thermostat, ThermostatMode
from env import get_project_id

debug = True
thermostat = None

def initialize():
    thermostat = Thermostat(
       projectId=get_project_id(),
       deviceName=None,
       debug=debug)
    thermostat.initialize()
    thermostat.set_temp(ThermostatMode.Cool, 76)
    return

if __name__ == '__main__':
  initialize()