"""Python package for reading AFP (Advanced Function Presentation) files.

   This module defines all the triplets supported by the package. Any other
   triplets will be parsed as SYNTAX_TRIPLET_RAW, i.e. we'll return their raw
   uninterpreted data.

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

# Parameter Names
PNAME_T_ID = 'Tid'
PNAME_T_LENGTH = 'Tlength'

# Any triplet not explicity defined
SYNTAX_TRIPLET_RAW = [
    fields.ParameterType(0,  0, fields.PTYPE_BYTE, 'Contents',  True,  None),
]

# To add new triplets:
# 1. Define its syntax here...

SYNTAX_TRIPLET_01 = [
    fields.ParameterType(0,  2, fields.PTYPE_CODE, 'GCSGID',    True,  None),
    fields.ParameterType(2,  2, fields.PTYPE_CODE, 'ID',        True,  None),
]

SYNTAX_TRIPLET_02 = [
    fields.ParameterType(0,  1, fields.PTYPE_CODE, 'FQNType',   True,  None),
    fields.ParameterType(1,  1, fields.PTYPE_CODE, 'FQNFmt',    True,  None),
    fields.ParameterType(2,  0, fields.PTYPE_CHAR, 'FQName',    True,  None),
]

SYNTAX_TRIPLET_18 = [
    fields.ParameterType(0,  1, fields.PTYPE_CODE, 'IStype',    True,  None),
    fields.ParameterType(1,  2, fields.PTYPE_CODE, 'ISid',      True,  None),
]

SYNTAX_TRIPLET_21 = [
    fields.ParameterType(0,  1, fields.PTYPE_CODE, 'ObjType',   True,  None),
    fields.ParameterType(1,  7, fields.PTYPE_CODE, 'ConData',   True,  None),
]

SYNTAX_TRIPLET_24 = [
    fields.ParameterType(0,  1, fields.PTYPE_CODE, 'ResType',   True,  None),
    fields.ParameterType(1,  1, fields.PTYPE_CODE, 'ResLID',   True,  None),
]

SYNTAX_TRIPLET_25 = [
    fields.ParameterType(0,  1, fields.PTYPE_CODE, 'ResSNum',   True,  None),
]

SYNTAX_TRIPLET_26 = [
    fields.ParameterType(0,  2, fields.PTYPE_CODE, 'CharRot',   True,  None),
]

SYNTAX_TRIPLET_2D = [
    fields.ParameterType(0,  4, fields.PTYPE_UBIN, 'DirByOff',  True,  None),
    fields.ParameterType(4,  4, fields.PTYPE_UBIN, 'DirByHi',   False, None),
]

SYNTAX_TRIPLET_36 = [
    fields.ParameterType(0,  2, fields.PTYPE_BYTE, 'Reserved',  True,  None),
    fields.ParameterType(2,  0, fields.PTYPE_CHAR, 'AttVal',    False, None),
]

SYNTAX_TRIPLET_56 = [
    fields.ParameterType(0,  4, fields.PTYPE_UBIN, 'PageNum',   True,  None),
]

SYNTAX_TRIPLET_57 = [
    fields.ParameterType(0,  4, fields.PTYPE_UBIN, 'ByteExt',   True,  None),
    fields.ParameterType(4,  4, fields.PTYPE_UBIN, 'BytExtHi',  True,  None),
]

SYNTAX_TRIPLET_58 = [
    fields.ParameterType(0,  4, fields.PTYPE_UBIN, 'SFOff',     True,  None),
    fields.ParameterType(4,  4, fields.PTYPE_UBIN, 'SFOffHi',   False, None),
]

SYNTAX_TRIPLET_59 = [
    fields.ParameterType(0,  4, fields.PTYPE_UBIN, 'SFExt',     True,  None),
    fields.ParameterType(4,  4, fields.PTYPE_UBIN, 'SFExtHi',   False, None),
]

SYNTAX_TRIPLET_62 = [
    fields.ParameterType(0,  1, fields.PTYPE_CODE, 'StampType', True,  None),
    fields.ParameterType(1,  1, fields.PTYPE_CODE, 'THunYear',  True,  None),
    fields.ParameterType(2,  2, fields.PTYPE_CODE, 'TenYear',   True,  None),
    fields.ParameterType(4,  3, fields.PTYPE_CODE, 'Day',       True,  None),
    fields.ParameterType(7,  2, fields.PTYPE_CODE, 'Hour',      True,  None),
    fields.ParameterType(9,  2, fields.PTYPE_CODE, 'Minute',    True,  None),
    fields.ParameterType(11, 2, fields.PTYPE_CODE, 'Second',    True,  None),
    fields.ParameterType(13, 2, fields.PTYPE_CODE, 'HundSec',   True,  None),
]

SYNTAX_TRIPLET_68 = [
    fields.ParameterType(0,  1, fields.PTYPE_CODE, 'MedOrient', True,  None),
]

SYNTAX_TRIPLET_80 = [
    fields.ParameterType(0,  4, fields.PTYPE_UBIN, 'SeqNum',    True,  None),
    fields.ParameterType(4,  4, fields.PTYPE_UBIN, 'LevNum',    True,  None),
]

# 2. Define its ID here...

TT_01 = 0x01
TT_02 = 0x02
TT_18 = 0x18
TT_21 = 0x21
TT_24 = 0x24
TT_25 = 0x25
TT_26 = 0x26
TT_2D = 0x2D
TT_36 = 0x36
TT_56 = 0x56
TT_57 = 0x57
TT_58 = 0x58
TT_59 = 0x59
TT_62 = 0x62
TT_68 = 0x68
TT_80 = 0x80

TripletType = collections.namedtuple('TripletType', ['name', 'syntax'])

# 3. Add it to the list here...

TRIPLET_TYPES = {
    TT_01: TripletType('Coded Graphic Character Set Global Identifier', SYNTAX_TRIPLET_01),
    TT_02: TripletType('Fully Qualified Name',                          SYNTAX_TRIPLET_02),
    TT_18: TripletType('MO:DCA Interchange Set',                        SYNTAX_TRIPLET_18),
    TT_21: TripletType('Resource Object Type',                          SYNTAX_TRIPLET_21),
    TT_24: TripletType('Resource Local Identifier',                     SYNTAX_TRIPLET_24),
    TT_25: TripletType('Resource Section Number',                       SYNTAX_TRIPLET_25),
    TT_26: TripletType('Character Rotation',                            SYNTAX_TRIPLET_26),
    TT_2D: TripletType('Object Byte Offset',                            SYNTAX_TRIPLET_2D),
    TT_36: TripletType('Attribute Value',                               SYNTAX_TRIPLET_36),
    TT_56: TripletType('Medium Map Page Number',                        SYNTAX_TRIPLET_56),
    TT_57: TripletType('Object Byte Extent',                            SYNTAX_TRIPLET_57),
    TT_58: TripletType('Object Structured Field Offset',                SYNTAX_TRIPLET_58),
    TT_59: TripletType('Object Structured Field Extent',                SYNTAX_TRIPLET_59),
    TT_62: TripletType('Local Date and Time Stamp',                     SYNTAX_TRIPLET_62),
    TT_68: TripletType('Medium Orientation',                            SYNTAX_TRIPLET_68),
    TT_80: TripletType('Attribute Qualifier',                           SYNTAX_TRIPLET_80),
}
