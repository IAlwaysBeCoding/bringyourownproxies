#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,UploadProblem

class CouldNotFindVar(AccountProblem):
    pass

class KummProblem(UploadProblem):
    pass
class NginxUploaderProblem(UploadProblem):
    pass

