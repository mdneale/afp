"""Python package for reading AFP (Advanced Function Presentation) files.

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

# Parser Interface
from .parser import stream
from .parser import load

# Exceptions
from .exceptions import *

# The explicitly-supported Structured Fields
from .fields import SF_TYPES
from .fields import SF_BAG
from .fields import SF_BDG
from .fields import SF_BDI
from .fields import SF_BDT
from .fields import SF_BFG
from .fields import SF_BFM
from .fields import SF_BMM
from .fields import SF_BNG
from .fields import SF_BPG
from .fields import SF_BPT
from .fields import SF_BRG
from .fields import SF_BRS
from .fields import SF_CTC
from .fields import SF_EAG
from .fields import SF_EDG
from .fields import SF_EDI
from .fields import SF_EDT
from .fields import SF_EFG
from .fields import SF_EFM
from .fields import SF_EMM
from .fields import SF_ENG
from .fields import SF_EPG
from .fields import SF_EPT
from .fields import SF_ERG
from .fields import SF_ERS
from .fields import SF_IEL
from .fields import SF_IPO
from .fields import SF_IPS
from .fields import SF_MCC
from .fields import SF_MCF
from .fields import SF_MCF_1
from .fields import SF_MDD
from .fields import SF_MMC
from .fields import SF_MPO
from .fields import SF_NOP
from .fields import SF_PGD
from .fields import SF_PGP_1
from .fields import SF_PTD
from .fields import SF_PTD_1
from .fields import SF_PTX
from .fields import SF_TLE

# Structured Field helper functions
from .fields import sfi_ext_flag
from .fields import sfi_seg_flag
from .fields import sfi_pad_flag

# The explicitly-supported Triplets
from .triplets import TRIPLET_TYPES

# The explicitly-supported Functions
from .functions import FUNCTIONS
from .functions import FN_U_AMB,  FN_C_AMB
from .functions import FN_U_AMI,  FN_C_AMI
from .functions import FN_U_BSU,  FN_C_BSU
from .functions import FN_U_DBR,  FN_C_DBR
from .functions import FN_U_DIR,  FN_C_DIR
from .functions import FN_U_ESU,  FN_C_ESU
from .functions import FN_U_RMB,  FN_C_RMB
from .functions import FN_U_RMI,  FN_C_RMI
from .functions import FN_U_RPS,  FN_C_RPS
from .functions import FN_U_SCFL, FN_C_SCFL
from .functions import FN_U_STC,  FN_C_STC
from .functions import FN_U_STO,  FN_C_STO
from .functions import FN_U_SVI,  FN_C_SVI
from .functions import FN_U_TRN,  FN_C_TRN
from .functions import FN_U_NOP,  FN_C_NOP
