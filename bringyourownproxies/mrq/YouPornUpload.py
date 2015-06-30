

from bringyourownproxies.sites import (YouPornAccount,YouPornVideoUploadRequest,
                                       YouPornTag,YouPornCategory,YouPornDescription,
                                        YouPornTitle,YouPornProfile,YouPornAuthor,
                                       YouPornComment,YouPornUpload)
from upload_task import UploadVideo


class Upload(UploadVideo):

    def run(self,params):
        super(Upload,self).run(params)
        print vars(self)


if __name__ == '__main__':
    upload = Upload()
    upload.run({})


