import re

from bringyourownproxies.parser import VideoParser
from bringyourownproxies.errors import VideoParserError
from bringyourownproxies.sites.motherless.properties import MotherlessComment


__all__ = ['MotherlessParser']

class MotherlessParser(VideoParser):

    def _extract_links_from_comment(self,html):

        links = []
        comment_doc = self.etree.fromstring(html,self.parser)

        for a in comment_doc.xpath('//a[@href]'):
            links.append((a.attrib['href'],a.text.strip()))

        return links

    def _get_all_text_from_comment(self,html):

        comment_doc = self.etree.fromstring(html,self.parser)
        all_text = comment_doc.xpath('//div[@style="text-align: justify;"]//text()')
        return "".join([txt.strip() for txt in all_text])

    def _get_all_comments(self,html):

        comments = []
        document = self.etree.fromstring(html,self.parser)
        comments_divs = document.xpath('//div[@class="media-comment"]')

        for comment in comments_divs:
            comment_html = self.tostring(comment)

            comment_doc = self.etree.fromstring(self.tostring(comment),self.parser)
            comment_posted_date = comment_doc.xpath('//div[@class="media-comment-meta"]')[0].text.strip()
            comment_id = comment.attrib['id'].replace('comment-','')
            comment_author = comment.attrib['rev']

            comment_links = self._extract_links_from_comment(html=comment_html)
            comment_text =  self._get_all_text_from_comment(html=comment_html)
            comments.append(MotherlessComment(author=comment_author,
                                              text=comment_text,
                                              comment_id=comment_id,
                                              posted_date=comment_posted_date,
                                              links=comment_links)
                            )


        return comments
    def _parse_uploaded_date(self,html):
        h2_doc = self.etree.fromstring(html,self.parser)
        return "".join([txt.
                        strip().
                        replace('Uploaded','')
                        for txt in h2_doc.xpath('//text()')])

    def _parse_views(self,html):
        h2_doc = self.etree.fromstring(html,self.parser)
        return "".join([txt.
                        strip().
                        replace('Views','').
                        replace(',','')
                        for txt in h2_doc.xpath('//text()')])

    def _parse_favorited(self,html):
        h2_doc = self.etree.fromstring(html,self.parser)
        return "".join([txt.
                        strip().
                        replace('Favorited','').
                        replace(',','')
                        for txt in h2_doc.xpath('//text()')])

    def get_video_stats(self,html,**kwargs):

        document = self.etree.fromstring(html,self.parser)
        comments = self._get_all_comments(html=html)

        first_big_row = document.xpath('//div[@id="media-info"]//div[@class="col-md-6 col-sm-12 col-xs-12"]')[0]
        second_big_row = document.xpath('//div[@id="media-info"]//div[@class="col-md-6 col-sm-12 col-xs-12"]')[1]

        f_big_doc = self.etree.fromstring(self.tostring(first_big_row),self.parser)
        s_big_doc = self.etree.fromstring(self.tostring(second_big_row),self.parser)

        author = f_big_doc.xpath('//div[@class="thumb-member-username"]/a')[0].text.strip()
        title = s_big_doc.xpath('//h1[@class="ellipsis gold"]')[0].text.strip()

        ellipsis_xpath = s_big_doc.xpath('//h2[@class="ellipsis"]')
        uploaded_date = self._parse_uploaded_date(html=self.tostring(ellipsis_xpath[0]))
        views = self._parse_views(html=self.tostring(ellipsis_xpath[1]))
        favorited = self._parse_favorited(html=self.tostring(ellipsis_xpath[2]))

        return {'comments':comments,
                'author':author,
                'uploaded_date':uploaded_date,
                'views':views,
                'title':title,
                'favorited':favorited}

    def get_download_url(self,html,**kwargs):

        found_download_url = re.search(r"__fileurl = '(.*?)';",html)
        if not found_download_url:
            raise VideoParserError('Could not find video download url for motherless' \
                                   ' video')
        return found_download_url.group(1)
