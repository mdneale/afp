"""Python package for reading AFP (Advanced Function Presentation) files.

   Exceptions raised by the parser.

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
"""

class Error(Exception):
    """Generic AFP parser exception."""
    pass

class ParseError(Error):
    """Exception while parsing the AFP stream."""

    # The error code from the AFP documentation
    # 0x00 means other error not described in the AFP documentation.
    modca_code = 0x00

    def __init__(self, message, field_no=None, field_start_offset=None):
        """
        Init with message and context.

        Arguments:
        message - The error message
        field_no - The field number in the file where the error occurred.
        field_start_offset - The byte number where the field begins.
        """
        super().__init__(message)
        self.field_no = field_no
        self.field_start_offset = field_start_offset

    def __str__(self):
        if self.modca_code == 0x00:
            s = super().__str__()
        else:
            s = '0x{0:02X} {1}'.format(self.modca_code, super().__str__())
        sep = ' -'
        if self.field_no is not None:
            s += '{0} field {1}'.format(sep, self.field_no)
            sep = ';'
        if self.field_start_offset is not None:
            s += '{0} start offset {1}'.format(sep, self.field_start_offset)
            sep = ';'
        return s

class EOFWhileReadingError(ParseError):
    pass

class InvalidStructuredFieldError(ParseError):
    pass

class RequiredParameterMissingError(ParseError):
    modca_code = 0x04

class EOSWhileReadingError(ParseError):
    pass

class UnrecognizedStructuredFieldError(ParseError):
    modca_code = 0x10

class PaddingNotImplementedError(ParseError):
    pass

class InvalidTripletError(ParseError):
    pass

class UnrecognizedTripletError(ParseError):
    modca_code = 0x10

class InvalidControlSequenceError(ParseError):
    pass

class UnknownFunctionError(ParseError):
    pass

class RepeatingGroupError(ParseError):
    pass

class UnrecognizedIdentifierCodeError(ParseError):
    modca_code = 0x40

class IncompleteParameterError(ParseError):
    modca_code = 0x02
