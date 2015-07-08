from bringyourownproxies.builders.errors import BuilderException

__all__ = ['BaseBuilder']

class BaseBuilder(object):

    klazz_builder_exception = BuilderException
    _site = None
    SITES = {}

    def __init__(self,site):

        if not self.is_site_supported(site):
            raise self.klazz_builder_exception('Site :{s} ' \
                                                'is not supported' \
                                                ''.format(s=site))
        self._site = site

    @property
    def site(self):
        return self._site

    def is_site_supported(self,site):
        supported = self.SITES.get(site,False)
        if supported == False:
            return False
        else:
            return True



