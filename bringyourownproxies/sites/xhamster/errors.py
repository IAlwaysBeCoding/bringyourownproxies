# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import VideoProblem

class FailedChangingThumbnailId(VideoProblem):
    pass

class VideoNotReadyForThumbnail(VideoProblem):
    pass
