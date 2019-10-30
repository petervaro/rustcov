#!/usr/bin/env python3
## INFO ##
## INFO ##

from re import compile, match
from subprocess import run, CalledProcessError, PIPE
from os import environ, listdir as list_dir
from os.path import getmtime as modified
from sys import argv

from toml import load


#------------------------------------------------------------------------------#
class FailedCommand(Exception): pass


#------------------------------------------------------------------------------#
def run_command(*command, env=None):
    try:
        run(command, check=True, stderr=PIPE, env=env)
    except CalledProcessError as error:
        raise FailedCommand(error.stderr) from None


#------------------------------------------------------------------------------#
def compile_tests():
    env = environ.copy()
    env.update({'RUSTFLAGS': '-Clink_dead_code'})
    run_command('cargo', 'test', '--no-run', env=env)


#------------------------------------------------------------------------------#
def executable_name():
    with open('Cargo.toml') as toml:
        return load(toml)['package']['name']


#------------------------------------------------------------------------------#
def find_latest_test_build():
    directory = 'target/debug'
    pattern = compile(rf"^{executable_name()}-[a-fA-F0-9]+$")
    latest = None
    for entry in list_dir(directory):
        if pattern.match(entry):
            entry = f'{directory}/{entry}'
            if (not latest or
                modified(latest) < modified(entry)):
                    latest = entry
    return latest


#------------------------------------------------------------------------------#
def generate_coverage():
    directory = 'target/coverage'
    run_command('rm', '-rf', directory)
    run_command('kcov', '--verify',
                        '--include-path=src',
                        directory,
                        find_latest_test_build())


#------------------------------------------------------------------------------#
def open_report():
    run_command('xdg-open', 'target/coverage/index.html')


#------------------------------------------------------------------------------#
if __name__ == '__main__':
    print('Compiling tests...')
    compile_tests()
    print('Generating coverage report...')
    generate_coverage()

    _, *arguments = argv
    if '--no-browser' not in arguments:
        print('Opening report...')
        open_report()
