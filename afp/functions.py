"""Python package for reading AFP (Advanced Function Presentation) files.

   This module defines all the presentation text control sequence functions
   supported by the package. Any other functions will be parsed as
   SYNTAX_FUNCTION_RAW, i.e. we'll return their raw uninterpreted data.

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

from . import fields

# Property Names
PNAME_CS_LENGTH = 'LENGTH'
PNAME_CS_TYPE = 'TYPE'

# Any function not explicity defined
SYNTAX_FUNCTION_RAW = [
    fields.ParameterType(0, 0, fields.PTYPE_BYTE, 'DATA',     True,  None),
]

# To add new functions:
# 1. Define its syntax here...

SYNTAX_FUNCTION_AMB = [
    fields.ParameterType(0, 2, fields.PTYPE_SBIN, 'DSPLCMNT', True,  None),
]

SYNTAX_FUNCTION_AMI = [
    fields.ParameterType(0, 2, fields.PTYPE_SBIN, 'DSPLCMNT', True,  None),
]

SYNTAX_FUNCTION_BSU = [
    fields.ParameterType(0, 1, fields.PTYPE_CODE, 'LID',      True,  None),
]

SYNTAX_FUNCTION_DBR = [
    fields.ParameterType(0, 2, fields.PTYPE_SBIN, 'RLENGTH',  True,  None),
    fields.ParameterType(2, 3, fields.PTYPE_SBIN, 'RWIDTH',   False, None),
]

SYNTAX_FUNCTION_DIR = [
    fields.ParameterType(0, 2, fields.PTYPE_SBIN, 'RLENGTH',  True,  None),
    fields.ParameterType(2, 3, fields.PTYPE_SBIN, 'RWIDTH',   False, None),
]

SYNTAX_FUNCTION_ESU = [
    fields.ParameterType(0, 1, fields.PTYPE_CODE, 'LID',      True,  None),
]

SYNTAX_FUNCTION_NOP = [
    fields.ParameterType(0, 0, fields.PTYPE_BYTE, 'IGNDATA',  False, None),
]

SYNTAX_FUNCTION_RMB = [
    fields.ParameterType(0, 2, fields.PTYPE_SBIN, 'INCRMENT', True,  None),
]

SYNTAX_FUNCTION_RMI = [
    fields.ParameterType(0, 2, fields.PTYPE_SBIN, 'INCRMENT', True,  None),
]

SYNTAX_FUNCTION_RPS = [
    fields.ParameterType(0, 2, fields.PTYPE_UBIN, 'RLENGTH',  True,  None),
    fields.ParameterType(2, 0, fields.PTYPE_CHAR, 'RPTDATA',  False, None),
]

SYNTAX_FUNCTION_SCFL = [
    fields.ParameterType(0, 1, fields.PTYPE_CODE, 'LID',      True,  None),
]

SYNTAX_FUNCTION_STC = [
    fields.ParameterType(0, 2, fields.PTYPE_CODE, 'FRGCOLOR', True,  None),
    fields.ParameterType(2, 1, fields.PTYPE_BYTE, 'PRECSION', False, None),
]

SYNTAX_FUNCTION_STO = [
    fields.ParameterType(0, 2, fields.PTYPE_CODE, 'IORNTION', True,  None),
    fields.ParameterType(2, 2, fields.PTYPE_CODE, 'BORNTION', True,  None),
]

SYNTAX_FUNCTION_SVI = [
    fields.ParameterType(0, 2, fields.PTYPE_SBIN, 'INCRMENT', True,  None),
]

SYNTAX_FUNCTION_TRN = [
    fields.ParameterType(0, 0, fields.PTYPE_CHAR, 'TRNDATA',  False, None),
]

Function = collections.namedtuple('Function', ['abbreviation', 'name', 'syntax'])

# 2. Define information about the function here - used for both the unchained
#    and chained versions.

FN_INFO_AMB =  Function('AMB',  'Absolute Move Baseline',                 SYNTAX_FUNCTION_AMB)
FN_INFO_AMI =  Function('AMI',  'Absolute Move Inline',                   SYNTAX_FUNCTION_AMI)
FN_INFO_BSU =  Function('BSU',  'Begin Suppression',                      SYNTAX_FUNCTION_BSU)
FN_INFO_DBR =  Function('DBR',  'Draw Baseline Rule',                     SYNTAX_FUNCTION_DBR)
FN_INFO_DIR =  Function('DIR',  'Draw Inline Rule',                       SYNTAX_FUNCTION_DIR)
FN_INFO_ESU =  Function('ESU',  'End Suppression',                        SYNTAX_FUNCTION_ESU)
FN_INFO_RMB =  Function('RMB',  'Relative Move Baseline',                 SYNTAX_FUNCTION_RMB)
FN_INFO_RMI =  Function('RMI',  'Relative Move Inline',                   SYNTAX_FUNCTION_RMI)
FN_INFO_RPS =  Function('RPS',  'Repeat String',                          SYNTAX_FUNCTION_RPS)
FN_INFO_SCFL = Function('SCFL', 'Set Coded Font Local',                   SYNTAX_FUNCTION_SCFL)
FN_INFO_STC =  Function('STC',  'Set Text Color',                         SYNTAX_FUNCTION_STC)
FN_INFO_STO =  Function('STO',  'Set Text Orientation',                   SYNTAX_FUNCTION_STO)
FN_INFO_SVI =  Function('SVI',  'Set Variable Space Character Increment', SYNTAX_FUNCTION_SVI)
FN_INFO_TRN =  Function('TRN',  'Transparent Data',                       SYNTAX_FUNCTION_TRN)
FN_INFO_NOP =  Function('NOP',  'No Operation',                           SYNTAX_FUNCTION_NOP)

# 3. Define its IDs here - one unchained and one chained...

# Unchained
FN_U_AMB  = 0xD2
FN_U_AMI  = 0xC6
FN_U_BSU  = 0xF2
FN_U_DBR  = 0xE6
FN_U_DIR  = 0xE4
FN_U_ESU  = 0xF4
FN_U_RMB  = 0xD4
FN_U_RMI  = 0xC8
FN_U_RPS  = 0xEE
FN_U_SCFL = 0xF0
FN_U_STC  = 0x74
FN_U_STO  = 0xF6
FN_U_SVI  = 0xC4
FN_U_TRN  = 0xDA
FN_U_NOP  = 0xF8

# Chained
FN_C_AMB  = 0xD3
FN_C_AMI  = 0xC7
FN_C_BSU  = 0xF3
FN_C_DBR  = 0xE7
FN_C_DIR  = 0xE5
FN_C_ESU  = 0xF5
FN_C_RMB  = 0xD5
FN_C_RMI  = 0xC9
FN_C_RPS  = 0xEF
FN_C_SCFL = 0xF1
FN_C_STC  = 0x75
FN_C_STO  = 0xF7
FN_C_SVI  = 0xC5
FN_C_TRN  = 0xDB
FN_C_NOP  = 0xF9

# 4. Add the unchained and chained versions to the list here...

FUNCTIONS = {
    FN_U_AMB:  FN_INFO_AMB,
    FN_U_AMI:  FN_INFO_AMI,
    FN_U_BSU:  FN_INFO_BSU,
    FN_U_DBR:  FN_INFO_DBR,
    FN_U_DIR:  FN_INFO_DIR,
    FN_U_ESU:  FN_INFO_ESU,
    FN_U_RMB:  FN_INFO_RMB,
    FN_U_RMI:  FN_INFO_RMI,
    FN_U_RPS:  FN_INFO_RPS,
    FN_U_SCFL: FN_INFO_SCFL,
    FN_U_STC:  FN_INFO_STC,
    FN_U_STO:  FN_INFO_STO,
    FN_U_SVI:  FN_INFO_SVI,
    FN_U_TRN:  FN_INFO_TRN,
    FN_U_NOP:  FN_INFO_NOP,

    FN_C_AMB:  FN_INFO_AMB,
    FN_C_AMI:  FN_INFO_AMI,
    FN_C_BSU:  FN_INFO_BSU,
    FN_C_DBR:  FN_INFO_DBR,
    FN_C_DIR:  FN_INFO_DIR,
    FN_C_ESU:  FN_INFO_ESU,
    FN_C_RMB:  FN_INFO_RMB,
    FN_C_RMI:  FN_INFO_RMI,
    FN_C_RPS:  FN_INFO_RPS,
    FN_C_SCFL: FN_INFO_SCFL,
    FN_C_STC:  FN_INFO_STC,
    FN_C_STO:  FN_INFO_STO,
    FN_C_SVI:  FN_INFO_SVI,
    FN_C_TRN:  FN_INFO_TRN,
    FN_C_NOP:  FN_INFO_NOP,
}

def unchained_function(function):
    """Return true if the function is unchained."""
    return function % 2 == 0

def chained_function(function):
    """Return true if the function is chained."""
    return not unchained_function(function)
