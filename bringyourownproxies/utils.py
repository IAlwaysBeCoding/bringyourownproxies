# -*- coding: utf-8 -*-
#!/usr/bin/python
import arrow

def show_printable_chars(text):
    return ''.join(i for i in text if ord(i)<128)

def generate_timestamp():
    utc = arrow.utcnow()
    return utc.timestamp
