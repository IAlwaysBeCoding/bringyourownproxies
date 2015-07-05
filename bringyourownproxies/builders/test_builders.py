
if __name__ == '__main__':
    from clint.textui.progress import Bar as ProgressBar
    from bringyourownproxies.builders.account import AccountBuilder
    from bringyourownproxies.builders.upload import UploadBuilder
    from bringyourownproxies.builders.video import VideoRequestBuilder
    from bringyourownproxies.builders.properties import CategoryBuilder
    import path
    site = 'xhamster'
    f = {'account':AccountBuilder(site),
         'upload':UploadBuilder(site),
         'video':VideoRequestBuilder(site)
        }
    username = 'tedwantsmore'
    password = 'money1003'
    email = 'tedwantsmore@gmx.com'
    description = 'Milf loves this anal'
    title = 'Big Boob Milf Loves Anal'
    categories = [{'name':'amateurd','category_type':'transsexual'}]
    tags  = ('anal','amateurd','milf')
    video_file = '/home/testfiles/milf_loves_anal.mp4'
    allow_comments = False
    category_type = 'transsexual'
    size = path.Path(video_file).size
    bar = ProgressBar(expected_size=size,filled_char='*')
    board = {'name':'girls','board_id':696286}
    category_builder = CategoryBuilder('xhamster')
    for c in categories:
        print c
        category = category_builder(**c)
        print type(category)
    def started(*args,**kwargs):
        video_upload_request = kwargs.get('video_upload_request')
        import time
        # at the beginning:
        start_time = time.time()


        print 'STARTED uploading video:{title}\n' \
                'tags:{tags}\n' \
                'category:{category}\n' \
                'description:{description}\n' \
                .format(title=video_upload_request.title,
                        tags=video_upload_request.tags,
                        category=video_upload_request.category,
                        description=video_upload_request.description)

    def uploading(*args,**kwargs):
        monitor = args[0]
        bar.show(monitor.bytes_read)
        #bar.show(monitor.bytes_read)

    def failed(*args,**kwargs):
        print 'FAILED'

    def finished(*args,**kwargs):
        print kwargs
        global start_time
        import time
        #print("it took %f seconds" % (time.time() - start_time))
        print 'FINISHED'



    request = f['video'].create_upload_request(video_file=video_file,
                                                description=description,
                                                title=title,
                                                tag=tags,
                                                category=categories,
                                                allow_comments=False,
                                                category_type=category_type,
                                                board=board)

    account = f['account'].create_account(username=username,
                                            password=password,
                                            email=email)

    upload = f['upload'].create_upload(account=account,
                                        video_upload_request=request,
                                        hooks={'started':started,
                                                 'uploading':uploading,
                                                 'failed':failed,
                                                 'finished':finished})

    #account.login()
    #account.save_cookies('/root/Dropbox/youporn_cookies.txt')
    account.load_cookies('/root/Dropbox/youporn_cookies.txt')
    print account.is_logined()
    #upload.start()
