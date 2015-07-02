

from bringyourownproxies.sites import (YouPornAccount,YouPornVideoUploadRequest,
                                       YouPornTag,YouPornCategory,YouPornDescription,
                                        YouPornTitle,YouPornProfile,YouPornAuthor,
                                       YouPornComment,YouPornUpload)

from upload_task import UploadVideo,UploadVideoException


class Upload(UploadVideo):

    def run(self,params):

        super(Upload,self).run(params)

        self.verify_account_works()


if __name__ == '__main__':
    upload = Upload()

    params = {}
    upload.run(params)


