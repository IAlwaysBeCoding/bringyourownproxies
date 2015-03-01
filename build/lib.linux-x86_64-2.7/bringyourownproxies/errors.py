#!/usr/bin/python


class VideoProblem(Exception):
    pass

class InvalidVideoUrl(VideoProblem):
    pass

class InvalidVideoParser(VideoProblem):
    pass

class InvalidVideoCallable(VideoProblem):
    pass

class InvalidVideoType(VideoProblem):
    pass

class VideoFileDoesNotExist(VideoProblem):
    pass

class InvalidVideoUploadRequest(VideoProblem):
    pass

class InvalidTitle(VideoProblem):
    pass

class InvalidTag(VideoProblem):
    pass

class InvalidCategory(VideoProblem):
    pass

class InvalidDescription(VideoProblem):
    pass

class FailedUpload(VideoProblem):
    pass

class FailedUpdatingVideoSettings(VideoProblem):
    pass

class HttpSettingsProblem(Exception):
    pass

class InvalidProxyList(HttpSettingsProblem):
    pass

class InvalidUserAgentList(HttpSettingsProblem):
    pass

class MissingValidSettings(HttpSettingsProblem):
    pass

class MissingValidProxySettings(HttpSettingsProblem):
    pass

class MissingValidUserAgentSettings(HttpSettingsProblem):
    pass

class AccountProblem(Exception):
    pass

class InvalidLogin(AccountProblem):
    pass

class AccountNotActivated(AccountProblem):
    pass

class NotLogined(AccountProblem):
    pass

class InvalidAccount(AccountProblem):
    pass

class ParsingProblem(Exception):
    pass

class CouldNotParseVideoUrl(ParsingProblem):
    pass
class CouldNotFindVar(ParsingProblem):
    pass
class CaptchaProblem(Exception):
    pass

class CaptchaRequired(CaptchaProblem):
    pass