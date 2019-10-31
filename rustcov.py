#!/usr/bin/env python3
## INFO ##
## INFO ##

from re import compile, match
from subprocess import run, CalledProcessError, PIPE
from os import environ, listdir as list_dir
from os.path import getmtime as modified, basename, splitext as split_ext
from argparse import ArgumentParser
from json import load as json_load

from toml import load as toml_load


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
        return toml_load(toml)['package']['name']


#------------------------------------------------------------------------------#
def find_latest_test_build(executable_name):
    directory = 'target/debug'
    pattern = compile(rf"^{executable_name}-[0-9a-fA-F]+$")
    latest = None
    for entry in list_dir(directory):
        if pattern.match(entry):
            entry = f'{directory}/{entry}'
            if (not latest or
                modified(latest) < modified(entry)):
                    latest = entry
    return latest


#------------------------------------------------------------------------------#
def print_one_line_coverage(prefix):
    with open(f'target/coverage/kcov-merged/coverage.json') as json:
        print(f"{prefix}: {json_load(json)['percent_covered']}")


#------------------------------------------------------------------------------#
def generate_coverage():
    directory = 'target/coverage/tests'
    run_command('rm', '-rf', directory)
    run_command('mkdir', '-p', directory)

    latest_build = find_latest_test_build(executable_name())
    kcov = 'kcov', '--verify', '--include-path=src', directory
    run_command(*kcov, latest_build)

    for test in list_dir('tests'):
        run_command(*kcov, find_latest_test_build(split_ext(test)[0]))

    run_command('kcov', '--merge', 'target/coverage', directory)
    run_command('rm', '-rf', directory)


#------------------------------------------------------------------------------#
def open_report():
    run_command('xdg-open', 'target/coverage/index.html')


#------------------------------------------------------------------------------#
if __name__ == '__main__':
    print('Compiling tests...')
    compile_tests()
    print('Generating coverage report...')
    generate_coverage()

    parser = ArgumentParser()
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--print-report', action='store')
    options = parser.parse_args()

    if not options.no_browser:
        print('Opening report...')
        open_report()

    if options.print_report:
        print_one_line_coverage(options.print_report)
