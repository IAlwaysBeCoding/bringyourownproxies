    #!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

class HardSexTubeAccount(_Account):
    
    SITE = 'HardSexTube'
    SITE_URL = 'www.hardsextube.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(HardSexTubeAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):

        attempt_login  = self._login(extra_post_vars={"remember_me": "1" if self.remember_me else "0"},
                                    ajax=True,
                                    post_url='http://www.hardsextube.com/login')

        result = attempt_login.json()
        
        if result['success']:
            return True
        else:
            if result['errorMessage'] == 'Username or password is incorrect':
                raise InvalidLogin('Wrong username or password')
            else:
                raise AccountProblem('Unknown problem while login into' \
                                    'Hardsextube message:{msg}'.format(msg=result['errorMessage']))
        raise AccountProblem('Unknown problem while login into Hardsextube')

    def is_logined(self):
        
        return self._is_logined(sign_out_xpath='//i[@class="icon icon-logout"]')

if __name__ == '__main__':
    account =  HardSexTubeAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()