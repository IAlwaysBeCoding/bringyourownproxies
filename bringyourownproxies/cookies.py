# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python


from requests.cookies import create_cookie
from tablib import Dataset

def read_cookies_from_yaml(filename):
    pass
def save_cookies_to_yaml(cookies,file_name):
    headers = ('domain','path','name','value')
    data = []
    for domain in cookies._cookies:
        for path in cookies._cookies[domain]:
            for cookie in cookies._cookies[domain][path]:
                cookie = cookies._cookies[domain][path][cookie]
                name = cookie.name
                value = cookie.value
                data.append((domain,path,name,value))

    dataset = Dataset(*data,headers=headers)
    with open(file_name,'w+') as f:
        f.write(dataset.yaml)
    return dataset