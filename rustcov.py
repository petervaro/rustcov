#!/usr/bin/env python3
## INFO ##
## INFO ##

from re import compile, match
from subprocess import run, CalledProcessError, PIPE
from os import environ, listdir as list_dir, walk
from os.path import (getmtime as modified,
                     basename,
                     splitext as split_ext,
                     join,
                     exists)
from argparse import ArgumentParser
from json import load as json_load
from logging import getLogger as get_logger, basicConfig as basic_config, DEBUG

from toml import load as toml_load


#------------------------------------------------------------------------------#
log = get_logger(__name__)


#------------------------------------------------------------------------------#
class FailedCommand(Exception): pass


#------------------------------------------------------------------------------#
def run_command(*command, env=None):
    try:
        log.debug(' '.join(command))
        run(command, check=True, stderr=PIPE, env=env)
    except CalledProcessError as error:
        raise FailedCommand(error.stderr) from None


#------------------------------------------------------------------------------#
def compile_tests():
    env = environ.copy()
    env.update({'RUSTFLAGS': '-Clink_dead_code'})
    run_command('cargo', 'test', '--all', '--no-run', env=env)


#------------------------------------------------------------------------------#
def executable_names(root='.'):
    with open(join(root, 'Cargo.toml')) as toml:
        toml = toml_load(toml)
        package_name = toml['package']['name']
        try:
            return package_name, toml['lib']['name']
        except KeyError:
            return (package_name, None)


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
    coverage_directory = 'target/coverage/tests'
    run_command('rm', '-rf', coverage_directory)
    run_command('mkdir', '-p', coverage_directory)

    for path, directories, files in walk('.'):
        # If this is the top-level of a rust project
        if 'Cargo.toml' in files:
            for directory in ('src', 'examples', 'target', '.git', 'tests'):
                try:
                    directories.remove(directory)
                except ValueError:
                    continue

            # If `src` is somehow missing from the top, skip this directory
            source = join(path, 'src')
            if not exists(source):
                continue

            command = ('kcov', '--verify',
                               f'--include-path={source}',
                               coverage_directory)

            # Get unit tests
            for executable_name in executable_names(path):
                latest_build = find_latest_test_build(executable_name)
                if latest_build:
                    run_command(*command, latest_build)
                    break

            # Get all the integration tests
            try:
                # TODO: Unfortunately Cargo does not use any sort of hierarchy
                #       or namespacing, which means if two members (or in fact
                #       the root) of a workspace have files or directories with
                #       the same name in their `tests` directories then those
                #       are going to be compiled at the same level under the
                #       same name in the shared `target` directory but with
                #       different _hash_ suffixes -- which makes it impossible
                #       to differentiate between them.  This means that for now
                #       `rustcov` will associate only one of the binaries with
                #       the correct source all the others will mismatch
                for test in list_dir(join(path, 'tests')):
                    latest_build = find_latest_test_build(split_ext(test)[0])
                    run_command(*command, latest_build)
            except FileNotFoundError:
                continue

    run_command('kcov', '--merge', 'target/coverage', coverage_directory)
    run_command('rm', '-rf', coverage_directory)


#------------------------------------------------------------------------------#
def open_report():
    run_command('xdg-open', 'target/coverage/index.html')


#------------------------------------------------------------------------------#
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--enable-log', action='store_true')
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--print-report', action='store')
    options = parser.parse_args()

    if options.enable_log:
        basic_config(level=DEBUG)

    print('Compiling tests...')
    compile_tests()
    print('Generating coverage report...')
    generate_coverage()

    if not options.no_browser:
        print('Opening report...')
        open_report()

    if options.print_report:
        print_one_line_coverage(options.print_report)
