import sys
import os.path

sys.path.insert(
    0, os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vendor')))

import click
import os

plugin_folder = os.path.join(os.path.dirname(__file__), 'tools')


class PerfkitCli(click.MultiCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, chain=True)

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']


cli = PerfkitCli(help='This tool\'s subcommands are loaded from a '
            'plugin folder dynamically.')


@cli.resultcallback()
def process_pipeline(tools):
    tested, *testers = tools

    if testers and isinstance(testers[0], list):
        testers = testers[0]

    tested.start()
    if testers:
        tested.ready()

    for tester in testers:
        tester.configure(tested)
        tester.start()
        tester.wait()
        print('.', end='', flush=True)

    print()
    print(', '.join(str(t.report()) for t in testers))

    tested.stop()


cli()
