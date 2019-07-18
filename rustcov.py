#!/usr/bin/env python3
## INFO ##
## INFO ##

from re import compile, match
from subprocess import run, CalledProcessError, PIPE
from os import listdir as list_dir
from os.path import getmtime as modified

from toml import load


#------------------------------------------------------------------------------#
class FailedCommand(Exception): pass


#------------------------------------------------------------------------------#
def run_command(*command):
    try:
        run(command, check=True, stderr=PIPE)
    except CalledProcessError as error:
        raise FailedCommand(error.stderr) from None


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
    run_command('kcov', '--verify',
                        '--include-path=src',
                        'target/coverage',
                        find_latest_test_build())


#------------------------------------------------------------------------------#
def open_report():
    run_command('xdg-open', 'target/coverage/index.html')


#------------------------------------------------------------------------------#
if __name__ == '__main__':
    generate_coverage()
    open_report()
