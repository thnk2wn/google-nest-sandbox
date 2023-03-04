
from thermostat import Thermostat, ThermostatMode
from env import get_project_id

import click

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

    thermostat = Thermostat(projectId=get_project_id(), deviceName=None, debug=debug)
    thermostat.initialize()
    ctx.obj['thermostat'] = thermostat

    pass

# python3 main.py --debug temp 75 --mode Heat
# python3 main.py temp 75 --mode Cool
@cli.command()
@click.pass_context
@click.option('--mode', required=True,
              type=click.Choice(['Cool', 'Heat'], case_sensitive=True))
@click.argument('temp', nargs=1, type=click.FLOAT)
def temp(ctx, temp: float, mode):
    modeType = ThermostatMode[mode]
    ctx.obj['thermostat'].set_temp(modeType, temp)

cli.add_command(temp)

if __name__ == '__main__':
    cli()