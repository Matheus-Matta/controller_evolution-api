# app_modulos/tasks.py
from celery import shared_task
import time

@shared_task
def slow_task():
    print('Started task, processing...')
    time.sleep(120)
    print('Finished Task')
    return True

