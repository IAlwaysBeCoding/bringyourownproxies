#!/usr/bin/python
def show_printable_chars(text):
    return ''.join(i for i in text if ord(i)<128)

def generate_timestamp():
    import time
    import random
    return int('{t}{ms}'.format(t=int(time.time()),ms=random.randrange(100,999,1)))
    

