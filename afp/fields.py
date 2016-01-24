"""Python package for reading AFP (Advanced Function Presentation) files.

   This module defines all the structured fields supported by the package. Any
   other structured fields will be parsed as SYNTAX_FIELD_RAW, i.e. we'll return
   their raw uninterpreted data.

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

import collections

# Data types
PTYPE_CODE    = 1
PTYPE_BYTE    = 2
PTYPE_UBIN    = 3
PTYPE_SBIN    = 4
PTYPE_CHAR    = 5
PTYPE_TRIPLET = 6
PTYPE_PTOCA   = 7

# Names of data types
PARAM_TYPE_NAMES = {
    PTYPE_CODE:    'CODE',
    PTYPE_BYTE:    'BYTE',
    PTYPE_UBIN:    'UBIN',
    PTYPE_SBIN:    'SBIN',
    PTYPE_CHAR:    'CHAR',
    PTYPE_TRIPLET: 'TRIPLET',
    PTYPE_PTOCA:   'PTOCA',
}

# Parameter Names
PNAME_EXT_DATA = 'ExtData'
PNAME_EXT_LENGTH = 'ExtLength'
PNAME_FLAG_BYTE = 'FlagByte'
PNAME_SF_LENGTH = 'SFLength'
PNAME_SF_TYPE_ID = 'SFTypeID'
PNAME_TRIPLETS = 'Triplets'

# A parameter of a structured field, triplet or control sequence function
# offset - The byte number where the parameter begins
# length - The number of bytes making up the parameter
# datatype - The data type of the parameter
# name - The name of the parameter.
# mandatory - True if the parameter must exist. Optional parameters must be
#             at the end.
# preproc - A preprocessor function to be called before parsing the parameter.
ParameterType = collections.namedtuple('ParameterType',
                                       ['offset', 'length', 'datatype', 'name', 'mandatory', 'preproc'])

# Parameter preprocess functions
# The existence of some of these mean special things to the parser, i.e. those
# are not really a preprocessor but a marker to indicate something special.
# If a preprocess function returns None, the parameter is skipped.
# Normally a preprocess function should return the parameter from the syntax
# being processed, i.e. the param argument.

def _next_group_length(sf, param):
    """Tells the parser that this parameter contains the length of the
    forthcoming repeating group.

    The length of some repeating groups are defined by a parameter placed before
    the repeating group, while others are defined by a parameter in the repeating
    group itself.

    Arguments:
    sf - A dictionary containing the structured field parsed so far
    param - The parameter in the syntax being processed

    Returns:
    The parameter in the syntax being processed.
    """
    return param

def _this_group_length(sf, param):
    """Tells the parser that this parameter contains the length of the current
    repeating group.

    The length of some repeating groups are defined by a parameter placed before
    the repeating group, while others are defined by a parameter in the repeating
    group itself.

    Arguments:
    sf - A dictionary containing the structured field parsed so far
    param - The parameter in the syntax being processed

    Returns:
    The parameter in the syntax being processed.
    """
    return param

def _suppress_if_no_extension(sf, param):
    """Suppress the parameter if the Structure Field Introducer has no extension.

    Arguments:
    sf - A dictionary containing the structured field parsed so far
    param - The parameter in the syntax being processed

    Returns:
    The parameter in the syntax being processed or None if we wish to suppress
    the parameter.
    """
    if sfi_ext_flag(sf[PNAME_FLAG_BYTE]):
        return param
    else:
        return None

def _set_extension_length(sf, param):
    """Return the Structured Field Introducer ExtData parameter with the correct
    length attribute set as found in the ExtLength parameter.

    Arguments:
    sf - A dictionary containing the structured field parsed so far
    param - The parameter in the syntax being processed

    Returns:
    The Structured Field Introducer ExtData parameter with the length attribute
    set, or None if the Structured Field Introducer has no extension.
    """
    if sfi_ext_flag(sf[PNAME_FLAG_BYTE]):
        return ParameterType(param.offset,
                             sf[PNAME_EXT_LENGTH] - 1,
                             param.datatype,
                             param.name,
                             param.mandatory,
                             param.preproc)
    else:
        return None

# Structured Field Introducer
SYNTAX_SFI = [
    ParameterType(0,  3,  PTYPE_CODE,    PNAME_SF_TYPE_ID, True,  None),
    ParameterType(3,  1,  PTYPE_BYTE,    PNAME_FLAG_BYTE,  True,  None),
    ParameterType(4,  2,  PTYPE_BYTE,    'Reserved',       True,  None),
    ParameterType(6,  1,  PTYPE_UBIN,    PNAME_EXT_LENGTH, True,  _suppress_if_no_extension),
    ParameterType(7,  0,  PTYPE_BYTE,    PNAME_EXT_DATA,   True,  _set_extension_length),
]

# Any structured field not explicity defined
SYNTAX_FIELD_RAW = [
    ParameterType(0,  0,  PTYPE_BYTE,    'Data',      False, None),
]

# To add new structued fields:
# 1. Define its syntax here...

SYNTAX_FIELD_BAG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'AEGName',      False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BDG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'DEGName',      False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BDI = [
    ParameterType(0,  8,  PTYPE_CHAR,    'IndxName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BDT = [
    ParameterType(0,  8,  PTYPE_CHAR,    'DocName',      True,  None),
    ParameterType(8,  2,  PTYPE_BYTE,    'Reserved',     True,  None),
    ParameterType(10, 0,  PTYPE_TRIPLET, PNAME_TRIPLETS, True,  None),
]

SYNTAX_FIELD_BFG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'FEGName',   False, None),
]

SYNTAX_FIELD_BFM = [
    ParameterType(0,  8,  PTYPE_CHAR,    'FMName',       False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BMM = [
    ParameterType(0,  8,  PTYPE_CHAR,    'MMName',       True,  None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BNG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'PGrpName',     True,  None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BPG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'PageName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BPT = [
    ParameterType(0,  8,  PTYPE_CHAR,    'PTdoName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BRG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'RGrpName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_BRS = [
    ParameterType(0,  8,  PTYPE_CHAR,    'RSName',       True,  None),
    ParameterType(8,  2,  PTYPE_BYTE,    'Reserved',     True,  None),
    ParameterType(10, 0,  PTYPE_TRIPLET, PNAME_TRIPLETS, True,  None),
]

SYNTAX_FIELD_CTC = [
    ParameterType(0,  10, PTYPE_BYTE,    'ConData',   True,  None),
]

SYNTAX_FIELD_EAG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'AEGName',   False, None),
]

SYNTAX_FIELD_EDG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'DEGName',   False, None),
]

SYNTAX_FIELD_EDI = [
    ParameterType(0,  8,  PTYPE_CHAR,    'IndxName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_EDT = [
    ParameterType(0,  8,  PTYPE_CHAR,    'DocName',      False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_EFG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'FEGName',   False, None),
]

SYNTAX_FIELD_EFM = [
    ParameterType(0,  8,  PTYPE_CHAR,    'FMName',    False, None),
]

SYNTAX_FIELD_EMM = [
    ParameterType(0,  8,  PTYPE_CHAR,    'MMName',    False, None),
]

SYNTAX_FIELD_ENG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'PGrpName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_EPG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'PageName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_EPT = [
    ParameterType(0,  8,  PTYPE_CHAR,    'PTdoName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_ERG = [
    ParameterType(0,  8,  PTYPE_CHAR,    'RGrpName',     False, None),
    ParameterType(8,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_ERS = [
    ParameterType(0,  8,  PTYPE_CHAR,    'RSName',    False, None),
]

SYNTAX_FIELD_IEL = [
    ParameterType(0,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, True,  None),
]

SYNTAX_FIELD_IPO = [
    ParameterType(0,  8,  PTYPE_CHAR,    'OvlyName',     True,  None),
    ParameterType(8,  3,  PTYPE_SBIN,    'XolOset',      True,  None),
    ParameterType(11, 3,  PTYPE_SBIN,    'YolOset',      True,  None),
    ParameterType(14, 2,  PTYPE_CODE,    'OvlyOrent',    False, None),
    ParameterType(16, 0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_IPS = [
    ParameterType(0,  8,  PTYPE_CHAR,    'PsegName',     True,  None),
    ParameterType(8,  3,  PTYPE_SBIN,    'XpsOset',      True,  None),
    ParameterType(11, 3,  PTYPE_SBIN,    'YpsOset',      True,  None),
    ParameterType(14, 0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_MCC = [
    [
        ParameterType(0,  2,  PTYPE_UBIN,    'Startnum', True,  None),
        ParameterType(2,  2,  PTYPE_UBIN,    'Stopnum',  True,  None),
        ParameterType(4,  1,  PTYPE_BYTE,    'Reserved', True,  None),
        ParameterType(5,  1,  PTYPE_CODE,    'MMCid',    True,  None),
    ],
]

SYNTAX_FIELD_MCF = [
    [
        ParameterType(0,  2,  PTYPE_UBIN,    'RGLength',     True,  _this_group_length),
        ParameterType(2,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, True,  None),
    ],
]

SYNTAX_FIELD_MCF_1 = [
    ParameterType(0,  1,  PTYPE_UBIN,    'RGLength',  True,  _next_group_length),
    ParameterType(1,  3,  PTYPE_BYTE,    'Reserved',  True,  None),
    [
        ParameterType(0,  1,  PTYPE_UBIN,    'CFLid',    True,  None),
        ParameterType(1,  1,  PTYPE_BYTE,    'Reserved', True,  None),
        ParameterType(2,  1,  PTYPE_CODE,    'Sectid',   True,  None),
        ParameterType(3,  1,  PTYPE_BYTE,    'Reserved', True,  None),
        ParameterType(4,  8,  PTYPE_CHAR,    'CFName',   True,  None),
        ParameterType(12, 8,  PTYPE_CHAR,    'CPName',   True,  None),
        ParameterType(20, 8,  PTYPE_CHAR,    'FCSName',  True,  None),
        ParameterType(28, 2,  PTYPE_CODE,    'CharRot',  False, None),
    ],
]

SYNTAX_FIELD_MDD = [
    ParameterType(0,  1,  PTYPE_CODE,    'XmBase',       True,  None),
    ParameterType(1,  1,  PTYPE_CODE,    'YmBase',       True,  None),
    ParameterType(2,  2,  PTYPE_UBIN,    'XmUnits',      True,  None),
    ParameterType(4,  2,  PTYPE_UBIN,    'YmUnits',      True,  None),
    ParameterType(6,  3,  PTYPE_UBIN,    'XmSize',       True,  None),
    ParameterType(9,  3,  PTYPE_UBIN,    'YmSize',       True,  None),
    ParameterType(12, 1,  PTYPE_BYTE,    'MDDFlgs',      True,  None),
    ParameterType(13, 0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_MMC = [
    ParameterType(0,  1,  PTYPE_CODE,    'MMCid',     True,  None),
    ParameterType(1,  1,  PTYPE_CODE,    'Constant',  True,  None),
    ParameterType(2,  0,  PTYPE_BYTE,    'Keywords',  False, None),
]

SYNTAX_FIELD_MPO = [
    [
        ParameterType(0,  2,  PTYPE_UBIN,    'RGLength',     True,  _this_group_length),
        ParameterType(2,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, True,  None),
    ],
]

SYNTAX_FIELD_NOP = [
    ParameterType(0,  0,  PTYPE_BYTE,    'UndfData',  False, None),
]

SYNTAX_FIELD_PGD = [
    ParameterType(0,  1,  PTYPE_CODE,    'XpgBase',      True,  None),
    ParameterType(1,  1,  PTYPE_CODE,    'YpgBase',      True,  None),
    ParameterType(2,  2,  PTYPE_UBIN,    'XpgUnits',     True,  None),
    ParameterType(4,  2,  PTYPE_UBIN,    'YpgUnits',     True,  None),
    ParameterType(6,  3,  PTYPE_UBIN,    'XpgSize',      True,  None),
    ParameterType(9,  3,  PTYPE_UBIN,    'YpgSize',      True,  None),
    ParameterType(12, 3,  PTYPE_BYTE,    'Reserved',     True,  None),
    ParameterType(15, 0,  PTYPE_TRIPLET, PNAME_TRIPLETS, False, None),
]

SYNTAX_FIELD_PGP_1 = [
    ParameterType(0,  3,  PTYPE_UBIN,    'XmOset',    True,  None),
    ParameterType(3,  3,  PTYPE_UBIN,    'YmOset',    True,  None),
]

SYNTAX_FIELD_PTD = [
    ParameterType(0,  1,  PTYPE_CODE,    'XPBASE',    True,  None),
    ParameterType(1,  1,  PTYPE_CODE,    'YPBASE',    True,  None),
    ParameterType(2,  2,  PTYPE_UBIN,    'XPUNITVL',  True,  None),
    ParameterType(4,  2,  PTYPE_UBIN,    'YPUNITVL',  True,  None),
    ParameterType(6,  3,  PTYPE_UBIN,    'XPEXTENT',  True,  None),
    ParameterType(9,  3,  PTYPE_UBIN,    'YPEXTENT',  True,  None),
    ParameterType(12, 2,  PTYPE_BYTE,    'TEXTFLAGS', False, None),
    ParameterType(14, 0,  PTYPE_BYTE,    'TXTCONDS',  False, None),
]

SYNTAX_FIELD_PTD_1 = [
    ParameterType(0,  1,  PTYPE_CODE,    'XptBase',   True,  None),
    ParameterType(1,  1,  PTYPE_CODE,    'YptBase',   True,  None),
    ParameterType(2,  2,  PTYPE_UBIN,    'XptUnits',  True,  None),
    ParameterType(4,  2,  PTYPE_UBIN,    'YptUnits',  True,  None),
    ParameterType(6,  2,  PTYPE_UBIN,    'XptSize',   True,  None),
    ParameterType(8,  2,  PTYPE_UBIN,    'YptSize',   True,  None),
    ParameterType(10, 2,  PTYPE_BYTE,    'Reserved',  False, None),
]

SYNTAX_FIELD_PTX = [
    ParameterType(0,  0,  PTYPE_PTOCA,   'PTOCAdat',  False, None),
]

SYNTAX_FIELD_TLE = [
    ParameterType(0,  0,  PTYPE_TRIPLET, PNAME_TRIPLETS, True,  None),
]

# 2. Define its ID here...

SF_BAG   = 0xD3A8C9
SF_BDG   = 0xD3A8C4
SF_BDI   = 0xD3A8A7
SF_BDT   = 0xD3A8A8
SF_BFG   = 0xD3A8C5
SF_BFM   = 0xD3A8CD
SF_BMM   = 0xD3A8CC
SF_BNG   = 0xD3A8AD
SF_BPG   = 0xD3A8AF
SF_BPT   = 0xD3A89B
SF_BRG   = 0xD3A8C6
SF_BRS   = 0xD3A8CE
SF_CTC   = 0xD3A79B
SF_EAG   = 0xD3A9C9
SF_EDG   = 0xD3A9C4
SF_EDI   = 0xD3A9A7
SF_EDT   = 0xD3A9A8
SF_EFG   = 0xD3A9C5
SF_EFM   = 0xD3A9CD
SF_EMM   = 0xD3A9CC
SF_ENG   = 0xD3A9AD
SF_EPG   = 0xD3A9AF
SF_EPT   = 0xD3A99B
SF_ERG   = 0xD3A9C6
SF_ERS   = 0xD3A9CE
SF_IEL   = 0xD3B2A7
SF_IPO   = 0xD3AFD8
SF_IPS   = 0xD3AF5F
SF_MCC   = 0xD3A288
SF_MCF   = 0xD3AB8A
SF_MCF_1 = 0xD3B18A
SF_MDD   = 0xD3A688
SF_MMC   = 0xD3A788
SF_MPO   = 0xD3ABD8
SF_NOP   = 0xD3EEEE
SF_PGD   = 0xD3A6AF
SF_PGP_1 = 0xD3ACAF
SF_PTD   = 0xD3B19B
SF_PTD_1 = 0xD3A69B
SF_PTX   = 0xD3EE9B
SF_TLE   = 0xD3A090

StructuredFieldType = collections.namedtuple('StructuredFieldType', ['abbreviation', 'name', 'syntax'])

# 3. Add it to the list here...

SF_TYPES = {
    SF_BAG:   StructuredFieldType('BAG',   'Begin Active Environment Group',             SYNTAX_FIELD_BAG),
    SF_BDG:   StructuredFieldType('BDG',   'Begin Document Environment Group',           SYNTAX_FIELD_BDG),
    SF_BDI:   StructuredFieldType('BDI',   'Begin Document Index',                       SYNTAX_FIELD_BDI),
    SF_BDT:   StructuredFieldType('BDT',   'Begin Document',                             SYNTAX_FIELD_BDT),
    SF_BFG:   StructuredFieldType('BFG',   'Begin Form Environment Group',               SYNTAX_FIELD_BFG),
    SF_BFM:   StructuredFieldType('BFM',   'Begin Form Map',                             SYNTAX_FIELD_BFM),
    SF_BMM:   StructuredFieldType('BMM',   'Begin Medium Map',                           SYNTAX_FIELD_BMM),
    SF_BNG:   StructuredFieldType('BNG',   'Begin Named Page Group',                     SYNTAX_FIELD_BNG),
    SF_BPG:   StructuredFieldType('BPG',   'Begin Page',                                 SYNTAX_FIELD_BPG),
    SF_BPT:   StructuredFieldType('BPT',   'Begin Presentation Text Object',             SYNTAX_FIELD_BPT),
    SF_BRG:   StructuredFieldType('BRG',   'Begin Resource Group',                       SYNTAX_FIELD_BRG),
    SF_BRS:   StructuredFieldType('BRS',   'Begin Resource',                             SYNTAX_FIELD_BRS),
    SF_CTC:   StructuredFieldType('CTC',   'Composed Text Control',                      SYNTAX_FIELD_CTC),
    SF_EAG:   StructuredFieldType('EAG',   'End Active Environment Group',               SYNTAX_FIELD_EAG),
    SF_EDG:   StructuredFieldType('EDG',   'End Document Environment Group',             SYNTAX_FIELD_EDG),
    SF_EDI:   StructuredFieldType('EDI',   'End Document Index',                         SYNTAX_FIELD_EDI),
    SF_EDT:   StructuredFieldType('EDT',   'End Document',                               SYNTAX_FIELD_EDT),
    SF_EFG:   StructuredFieldType('EFG',   'End Form Environment Group',                 SYNTAX_FIELD_EFG),
    SF_EFM:   StructuredFieldType('EFM',   'End Form Map',                               SYNTAX_FIELD_EFM),
    SF_EMM:   StructuredFieldType('EMM',   'End Medium Map',                             SYNTAX_FIELD_EMM),
    SF_ENG:   StructuredFieldType('ENG',   'End Named Page Group',                       SYNTAX_FIELD_ENG),
    SF_EPG:   StructuredFieldType('EPG',   'End Page',                                   SYNTAX_FIELD_EPG),
    SF_EPT:   StructuredFieldType('EPT',   'End Presentation Text Object',               SYNTAX_FIELD_EPT),
    SF_ERG:   StructuredFieldType('ERG',   'End Resource Group',                         SYNTAX_FIELD_ERG),
    SF_ERS:   StructuredFieldType('ERS',   'End Resource',                               SYNTAX_FIELD_ERS),
    SF_IEL:   StructuredFieldType('IEL',   'Index Element',                              SYNTAX_FIELD_IEL),
    SF_IPO:   StructuredFieldType('IPO',   'Include Page Overlay',                       SYNTAX_FIELD_IPO),
    SF_IPS:   StructuredFieldType('IPS',   'Include Page Segment',                       SYNTAX_FIELD_IPS),
    SF_MCC:   StructuredFieldType('MCC',   'Medium Copy Count',                          SYNTAX_FIELD_MCC),
    SF_MCF:   StructuredFieldType('MCF',   'Map Coded Font Format 2',                    SYNTAX_FIELD_MCF),
    SF_MCF_1: StructuredFieldType('MCF-1', 'Map Coded Font Format 1',                    SYNTAX_FIELD_MCF_1),
    SF_MDD:   StructuredFieldType('MDD',   'Medium Descriptor',                          SYNTAX_FIELD_MDD),
    SF_MMC:   StructuredFieldType('MMC',   'Medium Modification Control',                SYNTAX_FIELD_MMC),
    SF_MPO:   StructuredFieldType('MPO',   'Map Page Overlay',                           SYNTAX_FIELD_MPO),
    SF_NOP:   StructuredFieldType('NOP',   'No Operation',                               SYNTAX_FIELD_NOP),
    SF_PGD:   StructuredFieldType('PGD',   'Page Descriptor',                            SYNTAX_FIELD_PGD),
    SF_PGP_1: StructuredFieldType('PGP-1', 'Page Position Format 1',                     SYNTAX_FIELD_PGP_1),
    SF_PTD:   StructuredFieldType('PTD',   'Presentation Text Data Descriptor Format 2', SYNTAX_FIELD_PTD),
    SF_PTD_1: StructuredFieldType('PTD-1', 'Presentation Text Data Descriptor Format 1', SYNTAX_FIELD_PTD_1),
    SF_PTX:   StructuredFieldType('PTX',   'Presentation Text Data',                     SYNTAX_FIELD_PTX),
    SF_TLE:   StructuredFieldType('TLE',   'Tag Logical Element',                        SYNTAX_FIELD_TLE),
}

def sfi_ext_flag(b):
    """Return true if the Stuctured Field Introducer extension flag is set."""
    return b & 0b10000000 > 0

def sfi_seg_flag(b):
    """Return true if the Structured Field Introducer segmented flag is set."""
    return b & 0b00100000 > 0

def sfi_pad_flag(b):
    """Return true if the Stuctured Field Introducer padding flag is set."""
    return b & 0b00001000 > 0
