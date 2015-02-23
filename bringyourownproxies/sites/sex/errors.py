#!/usr/bin/python

from bringyourownproxies.errors import ParsingProblem,VideoProblem

class CouldNotParseFramePinUlr(ParsingProblem):
    pass

class MaxLimitVideoUpload(VideoProblem):
    pass
