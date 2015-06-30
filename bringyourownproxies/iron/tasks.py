from celery import Celery
import iron_celery



CELERY_RESULT_BACKEND = 'ironcache://5581dbf2a467f20006000093:J5A03FJdzjAgPeKWecFLx-UE1kw@'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
#CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
BROKER_URL = 'ironmq://5581dbf2a467f20006000093:J5A03FJdzjAgPeKWecFLx-UE1kw@'
app = Celery('test_app',
             broker=BROKER_URL,
             backend=CELERY_RESULT_BACKEND)

@app.task
def display_msg(msg):
    return 'Displaying msg:{m}'.format(m=msg)

if __name__ == '__main__':
   app.start()
