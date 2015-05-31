# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python

from bringyourownproxies.errors import VideoProblem


class VideoNotReadyForThumbnail(VideoProblem):
    pass

class FailedChangingThumbnailId(VideoProblem):
    pass