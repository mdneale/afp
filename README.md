# afp

Python package and utilities for reading AFP (Advanced Function Presentation)
files.

## License

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

## Overview

This repository contains an afp package for Python, allowing the caller to
read and decode AFP (Advanced Function Presentation) print files. For more
information on AFP see the website of the AFP Consortium http://afpcinc.org.

The repository also contains two utilities that make use of the library -
dumpafp.py and afp2ascii.py.

The code is pure Python 3 and was most recently tested on Python 3.4.1.

## dumpafp.py

This is a command-line utility to read an AFP file or files and output a
human-readable version. The detail of the AFP file is written to stdout or to a
file, allowing inspection of the AFP file. The utility is most useful for
debugging and investigating AFP files.

At its simplest you can execute the following:

    % python dumpafp.py myfile

More options are available, see:

    % python dumpafp.py --help

The utility and the afp package support a lot of the AFP spec and can decode
complex files, however not all structured fields, triplets and control sequences
defined by the AFP spec are implemented today. By default if an unknown
structured field, triplet or control sequence is encountered, the utility will
abort with an error. You can change this behaviour with the three command-line
options:

    --allow-unknown-fields
                      allow structured fields not supported by the parser in
                      the output

    --allow-unknown-functions
                      allow functions not supported by the parser in the
                      output

    --allow-unknown-triplets
                      allow triplets not supported by the parser in the
                      output

With these set, unknown entities are printed to the output for inspection in
their binary format, i.e. we do no decoding of the contents beyond decoding
the structured field introducer.

## afp2ascii.py

This utility is similar to dumpafp.py, except that it focuses on the text in
the AFP file rather than on all the detailed content. It is therefore good
for taking a quick look at an AFP file from the command-line, and good for
diff-ing AFP files. It is a very simple program and only covers very basic AFP
features.

To execute:

    % python afp2ascii.py myfile

More options are available, see:

    % python afp2ascii.py --help

It doesn't support the 'allow' options that dumpafp.py does - it always allows
unknown structured fields, triplets and control sequence functions.

## Package afp

The afp Python package implements the parser used by the above utilities.
At its simplest an AFP file can be opened and read using the code below:

    import afp
    with open('myfile', 'rb') as f:
        for sf in afp.stream(f):
            # Do something with structured field sf

The function afp.stream returns a generator allowing the caller to iterate over
the file without loading it all into memory. If you do wish to load the entire
file into memory you can use the afp.load function instead.

    import afp
    with open('myfile', 'rb') as f:
        fields = afp.load(f)
        for sf in fields:
            # Do something with structured field sf

The afp.stream and afp.load functions take optional arguments matching the
command-line options discussed above that control what to do when we come across
unknown structured fields, triplets or control sequence functions:

    def stream(f,
               allow_unknown_fields=False,
               allow_unknown_triplets=False,
               allow_unknown_functions=False,
               strict=False)

The fifth argument 'strict' causes the parser to be more strict when it comes
across missing parameters on structured fields, triplets or functions in the AFP
file; and incomplete parameters - where there are some but not enough bytes
left to read the parameter. By default the parameter is False allowing us to
be tolerant of slightly malformed AFP, and some older AFP files.

## What is not supported

The afp package does not implement the entire AFP spec, but it does implement
enough to cover many situations. The list below is a high-level view on what
is not implemented today.

1. Multiple structured fields, triplets and control sequences are not
   implemented. If you need to implement more, see the instructions in
   fields.py, triplets.py or functions.py - it's not difficult.

2. The optional record beginning marker is not supported. Files with no
   record beginning markers will fail with the error 'Missing 0x5A carriage
   control character'.

3. Structured Field padding is not supported. If an AFP file includes padding
   then it will fail with the error 'Structured Field padding is not supported'.

4. Writing AFP files. This would be a natural extension of the code we have
   already.
