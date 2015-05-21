#!/usr/bin/python

class Profile(object):

    def __init__(self,email=None,username=None,password=None,**kwargs):

        self.email = email
        self.username = username
        self.password = password

        super(Profile,self).__init__(**kwargs)

    def __repr__(self):
        return "<Profile Email:{email} Username:{username}"\
                "Password:{password}>".format(email=self.email,
                                            username=self.username,
                                            password=self.password)

class BasicProfile(object):

    def __init__(self,first_name=None,middle_name=None,last_name=None,gender=None,age=None,**kwargs):

        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.gender = gender
        self.age = age

        super(BasicProfile,self).__init__(**kwargs)

    def __repr__(self):

        return "<BasicProfile Name:{first_name} {middle_name_name} {last_name} " \
                "Gender:{gender}: Age:{age}> ".format(first_name=self.first_name,
                                                    middle_name_name=self.middle_name_name,
                                                    last_name=self.last_name,
                                                    gender=self.gender,
                                                    age=self.age)

class LocationProfile(object):

    def __init__(self,country=None,state=None,city=None,postal_code=None,county=None,address=None,**kwargs):

        self.country = country
        self.state = state
        self.county = county
        self.postal_code = postal_code
        self.city = city
        self.address = address

        super(LocationProfile,self).__init__(**kwargs)

    def __repr__(self):

        return "<LocationProfile Country:{country} State/Region:{state} " \
                "City:{city} ZipCode/PostalCode:{postal_code}" \
                "County:{county} Address:{address}> ".format(country=self.country,
                                                            state=self.state,
                                                            county=self.county,
                                                            postal_code=self.postal_code,
                                                            city=self.city,
                                                            address=self.address)



