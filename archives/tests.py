from django.test import TestCase
import datetime
from datetime import timedelta
# Create your tests here.

date =  datetime.datetime.now().year
dates =  datetime.datetime.now()

future =  datetime.datetime.now() + timedelta(days=7)

first = str(date-1)
date = str(date)

date = f'{first}/{date}'
print(int(date.split('/')[-1]))
