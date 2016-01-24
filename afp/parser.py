"""Python package for reading AFP (Advanced Function Presentation) files.

   The parser.

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

import logging

from . import exceptions
from . import fields
from . import functions
from . import triplets

logger = logging.getLogger(__name__)

CARRIAGE_CONTROL_CHAR = 0x5A
PTX_ESCAPE_SEQUENCE = 0x2BD3

# Parameter Names
PNAME_EXCEPTIONS = '_exceptions'
PNAME_REPEATING_GROUP = 'RepeatingGroup'

MODCA_CLASS_CODE = 0xD3

class ParserConfig:
    """Holds the configuration of the parser.

    allow_unknown_fields - If True, structured fields that the parser doesn't
                           know about are returned as raw data. If False an
                           exception is thrown and parsing is aborted.
    allow_unknown_triplets - If True, triplets that the parser doesn't
                             know about are returned as raw data. If False an
                             exception is thrown and parsing is aborted.
    allow_unknown_functions - If True, PTOCA functions that the parser doesn't
                              know about are returned as raw data. If False an
                              exception is thrown and parsing is aborted.
    strict - When strict is False, certain parse errors that would otherwise
             raise an exception and abort parsing, instead are added to the
             list of exceptions for the object being parsed and parsing continues.
             Errors that currently support this are RequiredParameterMissingError
             and IncompleteParameterError.
    """
    def __init__(self,
                 allow_unknown_fields=False,
                 allow_unknown_triplets=False,
                 allow_unknown_functions=False,
                 strict=False):
       self.allow_unknown_fields = allow_unknown_fields
       self.allow_unknown_triplets = allow_unknown_triplets
       self.allow_unknown_functions = allow_unknown_functions
       self.strict = strict

# The read_* functions are for reading data directly from a file.
# The later parse_* are for reading from a byte buffer.

def read_bytes(f, n):
    """Read n bytes from file f."""
    s = f.read(n)
    if len(s) == 0:
        return None
    if len(s) != n:
        raise exceptions.EOFWhileReadingError('Unexpected EOF while reading file')
    return [s[i] for i in range(0, len(s))]

def read_byte(f):
    """Read a byte from file f."""
    b = read_bytes(f, 1)
    if b is None:
        return None
    return b[0]

def read_ubin(f, n):
    """Read an unsigned binary number n bytes long from file f."""
    b = read_bytes(f, n)
    if b is None:
        return None
    u = 0
    for b in b:
        u = u << 8
        u += b
    return u

def syntax_length(syntax):
    """Return the number of bytes in a particular syntax definition.

    If the syntax has any optional parameters or parameters that have an
    undefined length then return zero.
    """
    length = 0
    for param in syntax:
        if not param.mandatory or param.length == 0:
            return 0
        length += param.length
    return length

def parse_bytes(data, n, offset=0):
    """Read n bytes from the byte buffer data starting at specified offset."""
    # An n value of zero means read rest of stream
    if n == 0:
        n = len(data) - offset
    if offset >= len(data):
        return None
    if offset + n > len(data):
        raise exceptions.EOSWhileReadingError('Out of data while parsing {0} byte(s) from offset {1} of {2}'.format(
            n,
            offset,
            data
        ))
    return [data[i] for i in range(offset, offset + n)]

def parse_ubin(data, n, offset=0):
    """Parse an unsigned binary number n bytes long from byte buffer data
    starting at specified offset.
    """
    b = parse_bytes(data, n, offset=offset)
    if b is None:
        return None
    u = 0
    for b in b:
        u = u << 8
        u += b
    return u

def parse_sbin(data, n, offset=0):
    """Parse a signed binary number n bytes long from byte buffer data
    starting at specified offset.
    """
    i = parse_ubin(data, n, offset=offset)
    if i is None:
        return None

    if i & (1 << ((n * 8) - 1)) != 0:
        i -= 1 << (n * 8)

    return i

def parse_code(data, n, offset=0):
    """Parse a code (effectively an unsigned binary number) n bytes long from
    byte buffer data starting at specified offset.
    """
    return parse_ubin(data, n, offset=offset)

def parse_chars(data, n, offset=0):
    """Parse text data n bytes long from byte buffer data starting at specified
    offset.
    """
    b = parse_bytes(data, n, offset=offset)
    if b is None:
        return None
    return bytes(b).decode('EBCDIC-CP-BE').strip()

def parse_triplets(data, parser_config, offset=0):
    """Parse triplets from byte buffer data starting at specified offset.
    Returns a list of triplets.
    """
    triplet_list = []
    p = offset
    i = 0
    # Keep going until we run out of data. Triplets are always at the end of a
    # structured field.
    while p < len(data):
        logger.debug('Parsing triplet {0}'.format(i + 1))
        t_length = parse_ubin(data, 1, offset=p)
        t_id = parse_code(data, 1, offset=p + 1)
        if t_id is None:
            raise exceptions.InvalidTripletError('Not enough data to parse triplet {0} Id'.format(i + 1))
        triplet_type = None
        # Check we know about the triplet type, and if we don't and we're not
        # allowing unknown triplets in parser output, raise an exception.
        if t_id in triplets.TRIPLET_TYPES:
            triplet_type = triplets.TRIPLET_TYPES[t_id]
        elif not parser_config.allow_unknown_triplets:
            raise exceptions.UnrecognizedTripletError('Unrecognized triplet 0x{0:02X}'.format(t_id))
        # Get the rest of the triplet data
        try:
            contents = parse_bytes(data, t_length - 2, offset=p + 2)
            if contents is None:
                raise exceptions.InvalidTripletError('Not enough data to parse triplet {0} contents'.format(i + 1))
        except exceptions.EOSWhileReadingError as e:
            raise exceptions.InvalidTripletError('Not enough data to parse triplet {0} contents'.format(i + 1))
        # Get the description of the triplet for debug output
        description = ''
        if triplet_type is not None:
            description = ' ({0})'.format(triplet_type.name)
        logger.debug('Triplet length {0} type 0x{1:02X}{2}'.format(t_length, t_id, description))
        # Parse the contents
        syntax = triplets.SYNTAX_TRIPLET_RAW
        if triplet_type is not None and triplet_type.syntax is not None:
            syntax = triplet_type.syntax
        triplet, bytes_processed = parse_syntax(contents, syntax, parser_config)
        triplet[triplets.PNAME_T_LENGTH] = t_length
        triplet[triplets.PNAME_T_ID] = t_id
        triplet_list.append(triplet)
        logger.debug('Triplet: {0}'.format(triplet))
        p += t_length
        i += 1
    return triplet_list

def parse_ptoca(data, parser_config, offset=0):
    """Parse PTOCA data from byte buffer data starting at specified offset.
    Returns a list control sequences.
    """
    ctrl_sequences = []
    # First is always unchained
    chained = False
    p = offset
    i = 0
    while p < len(data):
        logger.debug('Parsing control sequence {0}'.format(i + 1))
        if not chained:
            # Consume the escape sequence before an unchained control sequence
            try:
                escape_sequence = parse_ubin(data, 2, offset=p)
                p += 2
            except exceptions.EOSWhileReadingError as e:
                raise exceptions.InvalidControlSequenceError('Not enough data to parse control sequence {0} escape sequence'.format(i + 1))
            if escape_sequence != PTX_ESCAPE_SEQUENCE:
                raise exceptions.InvalidControlSequenceError('Missing 0x{0:X} escape sequence before control sequence {1}'.format(PTX_ESCAPE_SEQUENCE, i + 1))
        length = parse_ubin(data, 1, offset=p)
        if length is None:
            raise exceptions.InvalidControlSequenceError('Not enough data to parse control sequence {0} length'.format(i + 1))
        p += 1
        function = parse_ubin(data, 1, offset=p)
        if function is None:
            raise exceptions.InvalidControlSequenceError('Not enough data to parse control sequence {0} function'.format(i + 1))
        p += 1
        # Lookup the function. If we don't know what it is and we're not
        # allowing unknown functions then raise an exception.
        fn_info = None
        if function in functions.FUNCTIONS:
            fn_info = functions.FUNCTIONS[function]
        elif not parser_config.allow_unknown_functions:
            raise exceptions.UnknownFunctionError('Unknown function 0x{0:X}'.format(function))
        # Get the description of the triplet for debug output
        description = ''
        if fn_info is not None:
            description = ' ({0.abbreviation} {0.name})'.format(fn_info)
        logger.debug('Function length {0} type 0x{1:02X}{2}'.format(length, function, description))
        # Get the rest of the control sequence data
        try:
            function_data = parse_bytes(data, length - 2, offset=p)
            p += length - 2
            if function_data is None and length - 2 > 0:
                raise exceptions.InvalidControlSequenceError('Not enough data to parse control sequence {0} function data'.format(i + 1))
        except exceptions.EOSWhileReadingError as e:
            raise exceptions.InvalidControlSequenceError('Not enough data to parse control sequence {0} function data'.format(i + 1))
        # Parse the control sequence
        syntax = functions.SYNTAX_FUNCTION_RAW
        if fn_info is not None and fn_info.syntax is not None:
            syntax = fn_info.syntax
        ctrl_sequence, bytes_processed = parse_syntax(function_data, syntax, parser_config)
        ctrl_sequence[functions.PNAME_CS_LENGTH] = length
        ctrl_sequence[functions.PNAME_CS_TYPE] = function
        ctrl_sequences.append(ctrl_sequence)
        logger.debug('Control Sequence: {0}'.format(ctrl_sequence))
        chained = functions.chained_function(function)
        i += 1
    if chained:
        raise exceptions.InvalidControlSequenceError('Final function is chained')
    return ctrl_sequences

def _add_param(name, value, result, param_appearance_counters):
    """Add a parameter to the parse result dictionary.

    If the parameter name already exists in the dictionary then a counter
    is appended - e.g. myparam-2, myparam-3 etc.

    Arguments:
    name - The name of the parameter to add
    value - The value of the parameter to add
    result - The parse result dictionary to add the parameter to.
    param_appearance_counters - Dictionary that tracks how many times parameter
                                names have already been used.

    Returns:
    The unique name used in the dictionary for the param. Will be the name
    specified in the call to the function unless that name already existed in
    the dictionary, in which case it will have an incrementing number appended.
    """
    if name not in result:
        param_appearance_counters[name] = 1
        unique_name = name
    else:
        # Param name already exists - append a counter
        param_appearance_counters[name] += 1
        unique_name = '{0}-{1}'.format(name, param_appearance_counters[name])
    result[unique_name] = value
    return unique_name

def _add_exception(e, result):
    """Add an exception to the parse result.

    Exceptions are stored in the special key _exceptions, a list of exceptions.

    Arguments:
    e - The exception
    result - The parse result dictionary to add the exception to.
    """
    if PNAME_EXCEPTIONS not in result:
        result[PNAME_EXCEPTIONS] = []
    result[PNAME_EXCEPTIONS].append((e.modca_code, str(e)))

def parse_syntax(data, syntax, parser_config, result=None, param_appearance_counters=None):
    """Parse a syntax - this can be a structured field, a triplet or a PTOCA
    function.

    This is the heart of the parser. Syntaxes are lists of ParameterTypes and
    are defined in fields.py, triplets.py and functions.py.

    Arguments:
    data - A list of bytes to parse the data from.
    syntax - The sytax of the structured field, triplet or PTOCA function to
             use to parse the data.
    parser_config - A ParserConfig object.
    result - A dictionary to place the parser results in. If not None it is
             appended to.
    param_appearance_counters - Dictionary that tracks how many times parameter
                                names have been used in the result dictionary
                                so that parameters with the same names can be
                                given unique names with a number appended.

    Returns:
    Dictionary result containing all the data parsed and the number of bytes
    in the source data.
    """
    # The length of the upcoming repeating group
    next_group_length = 0
    next_field_offset = 0
    if result is None:
        result = {}
    if param_appearance_counters is None:
        param_appearance_counters = {}
    if data is None:
        data = []
    try:
        for param in syntax:
            if type(param) == list:
                # If parameter is a list then it is a repeating group

                # If we didn't get a length for the repeating group from an earlier parameter,
                # sum the lengths of the parameters in the repeating group.
                # This still may return zero if the group has optional parameters or if the
                # group has open-ended parameters. In this case we will expect the group to
                # define its own length with a parameter.
                if next_group_length == 0:
                    next_group_length = syntax_length(param)
                value = []
                repeating_group_offset = next_field_offset
                while repeating_group_offset < len(data):
                    if next_group_length != 0:
                        if repeating_group_offset + next_group_length > len(data):
                            raise exceptions.RepeatingGroupError('Repeating group length longer than available data')
                        repeating_group_data = data[repeating_group_offset:repeating_group_offset + next_group_length]
                    else:
                        repeating_group_data = data[repeating_group_offset:]
                    logger.debug('Parsing repeating group: offset {0}; length {1}'.format(repeating_group_offset,
                                                                                          next_group_length))
                    nested_group_result, bytes_processed = parse_syntax(repeating_group_data, param, parser_config)
                    value.append(nested_group_result)
                    repeating_group_offset += bytes_processed
                if len(value) > 0:
                    unique_name = _add_param(PNAME_REPEATING_GROUP, value, result, param_appearance_counters)
                    logger.debug('Parameter: {0} ({1}, 0) => <{2}>'.format(
                        unique_name,
                        next_field_offset,
                        value))
                # Reset the next repeating group length after we've processed the group
                next_group_length = 0
                next_field_offset = repeating_group_offset
            else:
                # Regular parameter
                if param.preproc is not None:
                    param = param.preproc(result, param)
                # Preprocessor function can return None to skip the field
                if param is not None:
                    value = None
                    if param.datatype == fields.PTYPE_CODE:
                        value = parse_code(data, param.length, offset=param.offset)
                    elif param.datatype == fields.PTYPE_BYTE:
                        value = parse_bytes(data, param.length, offset=param.offset)
                        if value is not None and param.length == 1:
                            value = value[0]
                    elif param.datatype == fields.PTYPE_UBIN:
                        value = parse_ubin(data, param.length, offset=param.offset)
                        if param.preproc is not None:
                            if param.preproc == fields._next_group_length:
                                # This parameter defines the length of the next group
                                if value == 0:
                                    raise exceptions.RepeatingGroupError('Repeating group length cannot be zero')
                                next_group_length = value
                            if param.preproc == fields._this_group_length:
                                # This parameter defines the length of the current group
                                if value == 0:
                                    raise exceptions.RepeatingGroupError('Repeating group length cannot be zero')
                                if value > len(data):
                                    raise exceptions.RepeatingGroupError('Repeating group length longer than available data')
                                data = data[0:value]
                    elif param.datatype == fields.PTYPE_SBIN:
                        value = parse_sbin(data, param.length, offset=param.offset)
                    elif param.datatype == fields.PTYPE_CHAR:
                        value = parse_chars(data, param.length, offset=param.offset)
                    elif param.datatype == fields.PTYPE_TRIPLET:
                        value = parse_triplets(data, parser_config, offset=param.offset)
                    elif param.datatype == fields.PTYPE_PTOCA:
                        value = parse_ptoca(data, parser_config, offset=param.offset)
                    if value is not None and (type(value) != list or len(value) != 0):
                        unique_name = _add_param(param.name, value, result, param_appearance_counters)
                        logger.debug('Parameter: {0} ({1}, {2}, {3}) => <{4}>'.format(
                            unique_name,
                            param.offset,
                            param.length,
                            fields.PARAM_TYPE_NAMES[param.datatype],
                            value))
                    elif param.mandatory:
                        e = exceptions.RequiredParameterMissingError('Required parameter missing: {0}'.format(param.name))
                        if parser_config.strict:
                            raise e
                        else:
                            _add_exception(e, result)
                            logger.warning(e)
                    next_field_offset = param.offset + param.length
    except exceptions.EOSWhileReadingError as e:
        if param.mandatory:
            e = exceptions.RequiredParameterMissingError('Required parameter missing: {0}'.format(param.name))
        else:
            e = exceptions.IncompleteParameterError('Not enough data to parse parameter {0}'.format(param.name))
        if parser_config.strict:
            raise e
        else:
            _add_exception(e, result)
            logger.warning(e)
    return result, len(data)

def read_structured_field(f, parser_config):
    """Read a structured field from file f.

    Returns a dictionary containing all the parameters of the structured field,
    including those of the structured field introducer.
    """
    sf = None
    # To keep count of appearances of parameters with the same name so we can
    # append a counter to make unique names.
    param_appearance_counters = {}
    # Read the record beginning marker
    b = read_byte(f)
    if b is not None:
        if b != CARRIAGE_CONTROL_CHAR:
            raise exceptions.InvalidStructuredFieldError('Missing 0x{0:02X} carriage control character'.format(
                CARRIAGE_CONTROL_CHAR))
        # Read the field length
        try:
            sf_length = read_ubin(f, 2)
            if sf_length is None:
                raise exceptions.InvalidStructuredFieldError('Missing structured field length')
        except exceptions.EOFWhileReadingError as e:
            raise exceptions.InvalidStructuredFieldError('Not enough data to read structured field length')
        logger.debug('Reading structured field length {0} bytes'.format(sf_length))
        # Read the rest of the field - excluding the 2 bytes for the length that
        # we've already read.
        try:
            data = read_bytes(f, sf_length - 2)
            if data is None:
                raise exceptions.InvalidStructuredFieldError('Structured field incorrect length')
        except exceptions.EOFWhileReadingError as e:
            raise exceptions.InvalidStructuredFieldError('Not enough data to read structured field')
        logger.debug('Structured Field data: {0}'.format(data))
        # Parse the Structured Field Introducer
        logger.debug('Parsing Structured Field Introducer')
        sf, bytes_processed = parse_syntax(data,
                                           fields.SYNTAX_SFI,
                                           parser_config,
                                           param_appearance_counters=param_appearance_counters)
        sf[fields.PNAME_SF_LENGTH] = sf_length
        if (sf[fields.PNAME_SF_TYPE_ID] & 0xFF0000) >> 16 != MODCA_CLASS_CODE:
            raise exceptions.UnrecognizedIdentifierCodeError('Unrecognized class code 0x{0:06X} - MO:DCA uses class code 0x{1:02X}'.format(sf[fields.PNAME_SF_TYPE_ID], MODCA_CLASS_CODE))
        # The parser doesn't currently support structured field padding
        if fields.sfi_pad_flag(sf[fields.PNAME_FLAG_BYTE]):
            raise exceptions.PaddingNotImplementedError('Structured Field padding is not supported')
        # Find the structured field type info
        sf_type = None
        if sf[fields.PNAME_SF_TYPE_ID] in fields.SF_TYPES:
            sf_type = fields.SF_TYPES[sf[fields.PNAME_SF_TYPE_ID]]
        elif not parser_config.allow_unknown_fields:
            raise exceptions.UnrecognizedStructuredFieldError('Unrecognized structured field 0x{0:06X}'.format(sf[fields.PNAME_SF_TYPE_ID]))
        description = ''
        if sf_type is not None:
            description = ' ({0.abbreviation} {0.name})'.format(sf_type)
        logger.debug("""    {0}: {1}
          {2}: 0x{3:06X}{4}
          {5}: 0x{6:02X}
              ExtFlag: {7}
              SegFlag: {8}
              PadFlag: {9}""".format(fields.PNAME_SF_LENGTH,
                                     sf[fields.PNAME_SF_LENGTH],
                                     fields.PNAME_SF_TYPE_ID,
                                     sf[fields.PNAME_SF_TYPE_ID],
                                     description,
                                     fields.PNAME_FLAG_BYTE,
                                     sf[fields.PNAME_FLAG_BYTE],
                                     fields.sfi_ext_flag(sf[fields.PNAME_FLAG_BYTE]),
                                     fields.sfi_seg_flag(sf[fields.PNAME_FLAG_BYTE]),
                                     fields.sfi_pad_flag(sf[fields.PNAME_FLAG_BYTE])))
        if fields.sfi_ext_flag(sf[fields.PNAME_FLAG_BYTE]):
            logger.debug("""    {0}: {1}
    {2}: {3}""".format(fields.PNAME_EXT_LENGTH,
                       sf[fields.PNAME_EXT_LENGTH],
                       fields.PNAME_EXT_DATA,
                       sf[fields.PNAME_EXT_DATA]))
        # Get the rest of the field data
        field_data_start = 6
        if fields.sfi_ext_flag(sf[fields.PNAME_FLAG_BYTE]):
            field_data_start += sf[fields.PNAME_EXT_LENGTH]
        field_data = data[field_data_start:]
        # Parse the field data
        syntax = fields.SYNTAX_FIELD_RAW
        if sf_type is not None and sf_type.syntax is not None:
            syntax = sf_type.syntax
        parse_syntax(field_data,
                     syntax,
                     parser_config,
                     result=sf,
                     param_appearance_counters=param_appearance_counters)
        logger.debug('Structured Field: {0}'.format(sf))
    return sf

def stream(f,
           allow_unknown_fields=False,
           allow_unknown_triplets=False,
           allow_unknown_functions=False,
           strict=False):
    """Interface to the parser. Parse AFP file f.

    Returns a generator so that the AFP file can be iterated-over without loading
    it all into memory. For example:

        with open('myfile', 'rb') as f:
            for sf in afp.stream(f):
                # Do something with structured field sf

    Open AFP files in binary as the encoding is not ASCII but EBCDIC.

    For the configuration arguments see the ParserConfig object at the top of
    this file.
    """
    field_no = 1
    parser_config = ParserConfig(allow_unknown_fields=allow_unknown_fields,
                                 allow_unknown_triplets=allow_unknown_triplets,
                                 allow_unknown_functions=allow_unknown_functions,
                                 strict=strict)
    logger.debug('Loading file {0}'.format(f.name))
    field_start_offset = f.tell()
    try:
        logger.debug('Reading structured field {0} at offset {1}'.format(field_no, field_start_offset))
        sf = read_structured_field(f, parser_config)
        while sf is not None:
            yield sf
            field_no += 1
            field_start_offset = f.tell()
            logger.debug('Reading structured field {0} at offset {1}'.format(field_no, field_start_offset))
            sf = read_structured_field(f, parser_config)
    except exceptions.ParseError as e:
        e.field_no = field_no
        e.field_start_offset = field_start_offset
        logger.error(e)
        raise e
    logger.debug('End of file {0}'.format(f.name))

def load(f,
         allow_unknown_fields=False,
         allow_unknown_triplets=False,
         allow_unknown_functions=False,
         strict=False):
    """Interface to the parser. Parse AFP file f.

    Returns a list of structured fields in the AFP file. Note that this causes
    the entire AFP file to be loaded into memory. If your AFP files are going to
    be big you may want to use the function stream instead. For example:

        with open('myfile', 'rb') as f:
            fields = afp.load(f)
            for sf in fields:
                # Do something with structured field sf

    Open AFP files in binary as the encoding is not ASCII but EBCDIC.

    For the configuration arguments see the ParserConfig object at the top of
    this file.
    """
    field_list = []
    for sf in stream(f,
                     allow_unknown_fields=allow_unknown_fields,
                     allow_unknown_triplets=allow_unknown_triplets,
                     allow_unknown_functions=allow_unknown_functions,
                     strict=strict):
        field_list.append(sf)
    return field_list
