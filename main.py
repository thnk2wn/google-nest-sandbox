
from thermostat import Thermostat, ThermostatMode
from env import get_project_id

import click

debug = True
thermostat = None


def initialize():
    print('Initializing')
    global thermostat
    thermostat = Thermostat(
        projectId=get_project_id(),
        deviceName=None,
        debug=debug)
    thermostat.initialize()
    return


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    initialize()
    pass

# python3 main.py --debug temp 75 --mode cool
# python3 main.py temp 75 --mode cool
@cli.command()
@click.pass_context
@click.option('--mode', required=True,
              type=click.Choice(['cool', 'heat'], case_sensitive=False))
@click.argument('temp', nargs=1, type=click.FLOAT)
def temp(ctx, temp: float, mode):
    debug = ctx.obj['DEBUG']
    click.echo(f"Debug is {debug}, set temp to {temp}, mode {mode}")
    global thermostat
    # TODO: mode parse
    thermostat.set_temp(ThermostatMode.Heat, temp)

cli.add_command(temp)

if __name__ == '__main__':
    cli()