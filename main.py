import test
from test import find_jobs_from


desired_characs = ['titles', 'companies', 'locations','links', 'details']

find_jobs_from('Glassdoor', 'Selenium', 'fulltime', desired_characs)
