# Google has a known bug with imports in the autogenerated grpc files.
# We need to add this directory to our PYHTONPATH
# See https://github.com/protocolbuffers/protobuf/issues/1491 for more details

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
