#!/usr/bin/python

from bringyourownproxies.errors import VideoProblem


class VideoNotReadyForThumbnail(VideoProblem):
    pass

class FailedChangingThumbnailId(VideoProblem):
    pass