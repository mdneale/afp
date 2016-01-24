#!/usr/bin/env python

"""Utility to read an AFP file or files and output an ASCII representation.

   This does not attempt to create an ASCII image of the document,
   rather it outputs all the text on the document and where it is printed.
   It is therefore much like dumpafp.py, however it is a litte more readable.

   This is an extremely simplistic utility and will only produce accurate output
   on the most simple of AFP files.

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

   usage: afp2ascii.py [-h] [--outfile OUTFILE] afp-file [afp-file ...]

   Read an AFP file or files and output an ASCII representation

   positional arguments:
     afp-file              an AFP file

   optional arguments:
     -h, --help            show this help message and exit
     --outfile OUTFILE, -o OUTFILE
                           the filename for the output (defaults to stdout)
"""

import afp
import argparse
import logging
import os
import sys

class Afp2AsciiError(Exception):
    """Generic exception for the module."""
    pass

class ProcessingContext:
    """Holds context information on where we are in the AFP document.

    When processing certain structured fields we need to know the context from
    previously-processed structured fields.
    """
    def __init__(self):
        # Whether we are within an AFP document - between BDT and EDT
        # structured fields
        self.in_document = False
        # The current Page - between BPG and EPG structured fields
        self.current_page = None

class Page:
    """A page"""
    def __init__(self):
        # Current inline position
        self.i = 0
        # Current baseline position
        self.b = 0
        # Current font
        self.font_local_id = 0xFF
        # Content to print
        self.content = []

def print_page(page, outfile=sys.stdout):
    """Print a single page to outfile."""
    print('--------------------------------------------------------------------------------', file=outfile)
    # Sort baseline (y), inline (x)
    page.content.sort()
    for (b, i, font_local_id, fn_type, data) in page.content:
        if fn_type in (afp.FN_C_TRN, afp.FN_U_TRN):
            # Transparent Data
            print('({0:4}, {1:4}): font={2:2}, text={3}'.format(b, i, font_local_id, data), file=outfile)
        elif fn_type in (afp.FN_C_DIR, afp.FN_U_DIR):
            # Draw Inline Rule
            print('({0:4}, {1:4}): inline draw length={2:5}, width={3:5}'.format(b, i, data[0], data[1]), file=outfile)
        elif fn_type in (afp.FN_C_DBR, afp.FN_U_DBR):
            # Draw Baseline Rule
            print('({0:4}, {1:4}): baseline draw length={2:5}, width={3:5}'.format(b, i, data[0], data[1]), file=outfile)
    print('--------------------------------------------------------------------------------', file=outfile)

def process_function(function, page):
    """Process a function in a control sequence and use it to alter the page."""
    if function['TYPE'] in (afp.FN_C_AMI, afp.FN_U_AMI):
        # Absolute Move Inline
        page.i = function['DSPLCMNT']
    elif function['TYPE'] in (afp.FN_C_AMB, afp.FN_U_AMB):
        # Absolute Move Baseline
        page.b = function['DSPLCMNT']
    elif function['TYPE'] in (afp.FN_C_RMI, afp.FN_U_RMI):
        # Relative Move Inline
        page.i += function['INCRMENT']
    elif function['TYPE'] in (afp.FN_C_RMB, afp.FN_U_RMB):
        # Relative Move Baseline
        page.b += function['INCRMENT']
    elif function['TYPE'] in (afp.FN_C_SCFL, afp.FN_U_SCFL):
        # Set Coded Font Local
        page.font_local_id = function['LID']
    elif function['TYPE'] in (afp.FN_C_TRN, afp.FN_U_TRN):
        # Transparent Data
        page.content.append((page.b,
                             page.i,
                             page.font_local_id,
                             function['TYPE'],
                             function['TRNDATA']))
    elif function['TYPE'] in (afp.FN_C_DIR, afp.FN_U_DIR):
        # Draw Inline Rule
        page.content.append((page.b,
                             page.i,
                             page.font_local_id,
                             function['TYPE'],
                             (function['RLENGTH'], function['RWIDTH'])))
    elif function['TYPE'] in (afp.FN_C_DBR, afp.FN_U_DBR):
        # Draw Baseline Rule
        page.content.append((page.b,
                             page.i,
                             page.font_local_id,
                             function['TYPE'],
                             (function['RLENGTH'], function['RWIDTH'])))

def process_field(sf, context, outfile=sys.stdout):
    """Process a structured field and alter the context accordingly."""
    if sf['SFTypeID'] == afp.SF_BDT:
        # Begin Document
        if context.in_document:
            raise Afp2AsciiError('Stream contains nested documents')
        context.in_document = True
        print('================================================================================', file=outfile)
    elif sf['SFTypeID'] == afp.SF_BPG:
        # Begin Page
        if context.current_page is not None:
            raise Afp2AsciiError('Stream contains nested pages')
        context.current_page = Page()
    elif sf['SFTypeID'] == afp.SF_PTX:
        # Presentation Text Data
        for function in sf['PTOCAdat']:
            process_function(function, context.current_page)
    elif sf['SFTypeID'] == afp.SF_EPG:
        # End Page
        if context.current_page is None:
            raise Afp2AsciiError('End page before begin')
        print_page(context.current_page, outfile)
        context.current_page = None
    elif sf['SFTypeID'] == afp.SF_EDT:
        # End Document
        if not context.in_document:
            raise Afp2AsciiError('End document before begin')
        context.in_document = False
        print('================================================================================', file=outfile)

def afp_to_ascii(infile, outfile=sys.stdout):
    """Print a single AFP file 'infile' to the output 'outfile'."""
    context = ProcessingContext()
    for sf in afp.stream(infile,
                         allow_unknown_fields=True,
                         allow_unknown_triplets=True,
                         allow_unknown_functions=True):
        process_field(sf, context, outfile)

def multiple_afp_to_ascii(afp_files, outfile=sys.stdout):
    """Print multiple AFP files specified by filename 'afp_files' to the output
    'outfile'.
    """
    for filename in afp_files:
        with open(filename, 'rb') as infile:
            if len(afp_files) > 1:
                print('File: {0}'.format(filename), file=outfile)
            afp_to_ascii(infile, outfile=outfile)

def parse_command_line():
    """Parse the utility's command-line arguments."""
    parser = argparse.ArgumentParser(description='Read an AFP file or files and output an ASCII representation')
    parser.add_argument(
        'afp_files',
        metavar='afp-file',
        nargs='+',
        help='an AFP file')
    parser.add_argument(
        '--outfile', '-o',
        dest='outfile',
        help='the filename for the output (defaults to stdout)')
    return parser.parse_args()

def main():
    args = parse_command_line()
    logging.basicConfig(level=logging.FATAL, format='%(levelname)s %(message)s')
    try:
        if args.outfile is None:
            multiple_afp_to_ascii(args.afp_files)
        else:
            with open(args.outfile, 'w') as outfile:
                multiple_afp_to_ascii(args.afp_files, outfile=outfile)
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
    except Afp2AsciiError as e:
        print('{0}: error: {1}'.format(os.path.basename(sys.argv[0]), str(e).lower()), file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        # Exit quietly on ctrl-c
        exit(1)

if __name__ == '__main__':
    main()
