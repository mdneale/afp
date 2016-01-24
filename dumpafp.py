#!/usr/bin/env python

"""Utility to read an AFP file or files and output a human-readable version.

   Copyright 2016 Matthew NEALE

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   usage: dumpafp.py [-h] [--allow-unknown-fields] [--allow-unknown-functions]
                     [--allow-unknown-triplets] [--debug] [--outfile OUTFILE]
                     [--strict] [--warn]
                     afp-file [afp-file ...]

   Read an AFP file or files and output a human-readable version

   positional arguments:
     afp-file              an AFP file

   optional arguments:
     -h, --help            show this help message and exit
     --allow-unknown-fields
                           allow structured fields not supported by the parser in
                           the output
     --allow-unknown-functions
                           allow functions not supported by the parser in the
                           output
     --allow-unknown-triplets
                           allow triplets not supported by the parser in the
                           output
     --debug               print debugging information to stderr
     --outfile OUTFILE, -o OUTFILE
                           the filename for the output (defaults to stdout)
     --strict              enable strict parsing - missing mandatory fields are
                           not allowed
     --warn                print warning information to stderr
"""

import afp
import argparse
import logging
import os
import sys

def print_line(text, indent=0, file=sys.stdout):
    """Print a line of output indented by a specified number of characters."""
    print('{0:<{width}}{1}'.format('', text, width=indent), file=file)

def print_params(params, ignore=(), indent=0, file=sys.stdout):
    """Print the parameters of a structured field, a triplet or a PTOCA control
    sequence.

    Arguments:
    params - A dictionary containing the parameters to print.
    ignore - A list of parameter names to suppress.
    indent - The number of characters to indent any text printed.
    file - The file to print the output to.
    """
    for name, value in params.items():
        if name == 'Triplets':
            print_line('{0}:'.format(name), indent=indent, file=file)
            i = 1
            for triplet in value:
                print_line('__Triplet {0}__'.format(i), indent=indent + 4, file=file)
                t_type = None
                description = ''
                if triplet['Tid'] in afp.TRIPLET_TYPES:
                    t_type = afp.TRIPLET_TYPES[triplet['Tid']]
                    description = ' ({0.name})'.format(t_type)
                print_line('Tlength: {0}'.format(triplet['Tlength']), indent=indent + 4, file=file)
                print_line('Tid: 0x{0:02X}{1}'.format(triplet['Tid'], description), indent=indent + 4, file=file)
                print_params(triplet, ignore=('Tlength', 'Tid'), indent=indent + 4, file=file)
                i += 1
        elif name == 'RepeatingGroup':
            print_line('{0}:'.format(name), indent=indent, file=file)
            i = 1
            for group in value:
                print_line('__Group {0}__'.format(i), indent=indent + 4, file=file)
                print_params(group, indent=indent + 4, file=file)
                i += 1
        elif name == 'PTOCAdat':
            print_line('{0}:'.format(name), indent=indent, file=file)
            i = 1
            for function in value:
                print_line('__Function {0}__'.format(i), indent=indent + 4, file=file)
                fn_type = None
                description = ''
                if function['TYPE'] in afp.FUNCTIONS:
                    fn_type = afp.FUNCTIONS[function['TYPE']]
                    description = ' ({0.abbreviation} {0.name})'.format(fn_type)
                print_line('LENGTH: {0}'.format(function['LENGTH']), indent=indent + 4, file=file)
                print_line('{0}: 0x{1:02X}{2}'.format('TYPE', function['TYPE'], description), indent=indent + 4, file=file)
                print_params(function, ignore=('LENGTH', 'TYPE'), indent=indent + 4, file=file)
                i += 1
        elif name not in ignore:
            print_line('{0}: {1}'.format(name, value), indent=indent, file=file)

def print_structured_field(sf, file=sys.stdout):
    """Print a structured field to the output."""
    sf_type = None
    description = ''
    if sf['SFTypeID'] in afp.SF_TYPES:
        sf_type = afp.SF_TYPES[sf['SFTypeID']]
        description = ' ({0.abbreviation} {0.name})'.format(sf_type)
    print_line('SFLength: {0}'.format(sf['SFLength']), file=file)
    print_line('SFTypeID: 0x{0:06X}{1}'.format(sf['SFTypeID'], description), file=file)
    print_line('FlagByte: 0x{0:02X}'.format(sf['FlagByte']), file=file)
    print_line('ExtFlag: {0}'.format(afp.sfi_ext_flag(sf['FlagByte'])), indent=4, file=file)
    print_line('SegFlag: {0}'.format(afp.sfi_seg_flag(sf['FlagByte'])), indent=4, file=file)
    print_line('PadFlag: {0}'.format(afp.sfi_pad_flag(sf['FlagByte'])), indent=4, file=file)
    print_line('Reserved: {0}'.format(sf['Reserved']), file=file)
    if afp.sfi_ext_flag(sf['FlagByte']):
        print_line('ExtLength: {0}'.format(sf['ExtLength']), file=file)
        print_line('ExtData: {0}'.format(sf['ExtData']), file=file)
    print_params(sf, ignore=('SFLength', 'SFTypeID', 'FlagByte', 'Reserved', '_exceptions'), file=file)

def dump_afp_file(infile,
                  outfile=sys.stdout,
                  allow_unknown_fields=False,
                  allow_unknown_triplets=False,
                  allow_unknown_functions=False,
                  strict=False):
    """Print a single AFP file 'infile' to the output 'outfile'."""
    i = 1
    for sf in afp.stream(infile,
                         allow_unknown_fields=allow_unknown_fields,
                         allow_unknown_triplets=allow_unknown_triplets,
                         allow_unknown_functions=allow_unknown_functions,
                         strict=strict):
        print_line('__Structured Field {0}__'.format(i), file=outfile)
        print_structured_field(sf, file=outfile)
        i += 1

def dump_afp_files(afp_files,
                   outfile=sys.stdout,
                   allow_unknown_fields=False,
                   allow_unknown_triplets=False,
                   allow_unknown_functions=False,
                   strict=False):
    """Print multiple AFP files specified by filename 'afp_files' to the output
    'outfile'.
    """
    for filename in afp_files:
        with open(filename, 'rb') as infile:
            if len(afp_files) > 1:
                print_line('__File {0}__'.format(filename), file=outfile)
            dump_afp_file(infile,
                          outfile=outfile,
                          allow_unknown_fields=allow_unknown_fields,
                          allow_unknown_triplets=allow_unknown_triplets,
                          allow_unknown_functions=allow_unknown_functions,
                          strict=strict)

def parse_command_line():
    """Parse the utility's command-line arguments."""
    parser = argparse.ArgumentParser(description='Read an AFP file or files and output a human-readable version')
    parser.add_argument(
        'afp_files',
        metavar='afp-file',
        nargs='+',
        help='an AFP file')
    parser.add_argument(
        '--allow-unknown-fields',
        dest='allow_unknown_fields',
        action='store_true',
        help='allow structured fields not supported by the parser in the output')
    parser.add_argument(
        '--allow-unknown-functions',
        dest='allow_unknown_functions',
        action='store_true',
        help='allow functions not supported by the parser in the output')
    parser.add_argument(
        '--allow-unknown-triplets',
        dest='allow_unknown_triplets',
        action='store_true',
        help='allow triplets not supported by the parser in the output')
    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='print debugging information to stderr')
    parser.add_argument(
        '--outfile', '-o',
        dest='outfile',
        help='the filename for the output (defaults to stdout)')
    parser.add_argument(
        '--strict',
        dest='strict',
        action='store_true',
        help='enable strict parsing - missing mandatory fields are not allowed')
    parser.add_argument(
        '--warn',
        dest='warn',
        action='store_true',
        help='print warning information to stderr')
    return parser.parse_args()

def main():
    args = parse_command_line()
    # Set logging level based upon --debug command-line argument
    if args.debug:
        log_level = logging.DEBUG
    elif args.warn:
        log_level = logging.WARNING
    else:
        log_level = logging.FATAL
    logging.basicConfig(level=log_level, format='%(levelname)s %(message)s')
    try:
        if args.outfile is None:
            dump_afp_files(args.afp_files,
                           allow_unknown_fields=args.allow_unknown_fields,
                           allow_unknown_triplets=args.allow_unknown_triplets,
                           allow_unknown_functions=args.allow_unknown_functions,
                           strict=args.strict)
        else:
            with open(args.outfile, 'w') as outfile:
                dump_afp_files(args.afp_files,
                               outfile=outfile,
                               allow_unknown_fields=args.allow_unknown_fields,
                               allow_unknown_triplets=args.allow_unknown_triplets,
                               allow_unknown_functions=args.allow_unknown_functions,
                               strict=args.strict)
    except FileNotFoundError as e:
        print('{0}: error: {1}'.format(os.path.basename(sys.argv[0]), str(e).lower()), file=sys.stderr)
        exit(1)
    except BrokenPipeError as e:
        # If we pipe the output to a utility such as head we will get a BrokenPipeError
        # when head closes stdout. Ignore that error here.

        # Close stdout explicitly otherwise we get an error when it closes during
        # shutdown.
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        # We deem this process has done its work so exit successfully
        exit(0)
    except afp.Error as e:
        print('{0}: error: {1}'.format(os.path.basename(sys.argv[0]), str(e).lower()), file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        # Exit quietly on ctrl-c
        exit(1)

if __name__ == '__main__':
    main()
