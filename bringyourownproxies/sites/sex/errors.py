# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python

from bringyourownproxies.errors import ParsingProblem,VideoProblem

class CouldNotParseFramePinUlr(ParsingProblem):
    pass

class MaxLimitVideoUpload(VideoProblem):
    pass

class BoardProblem(Exception):
    pass

class BoardAlreadyTaken(BoardProblem):
    pass
