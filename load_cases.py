import os
import random
import asyncio
from dotenv import load_dotenv
from supabase import create_client
from faker import Faker

fake = Faker()
load_dotenv()

status_vals = {'rejected': 'Rejected', 'active': 'Active', 'closed': 'Closed', 
               'invest_assigned':'Investigator Assigned', 'court_scheduled': 'Court Scheduled'}

# Turn into dict with client code
pd_vals = {'Peddleton PD': '37591', 'Acadia PD': '27402', ' Snowview PD': '29470', 'Goldburgh PD': '02749',
           'Casterley PD': '13754', 'North Lexington PD': '83242', 'Hardford PD': '24213', 'Lakegaard PD': '26183', 
           'Rosefolke PD': '14163','Greenhove PD': '35416', 'Springhoff PD': '23432', 'Blackwood PD': '48282', 
           'Canyon Valley PD': '12352'}

case_type = ['Arson', 'Kidnapping', 'Larceny', 'Shooting', 'Assault', 'Burglary', 'Carjacking',
             'Murder', 'DUI', 'Robbery', 'Auto Theft', 'Shoplifting']

class Database:
  def __init__(self):
    self.url = os.getenv("SUPA_PROJECT_URL")
    self.key = os.getenv("SUPA_SERVICE_ROLE")
    self.client = create_client(self.url, self.key)

class Victim:
  def __init__(self):
    self.id = str(fake.unique.random_number(digits=8))
    self.name = fake.first_name() + ' ' + fake.last_name()
    self.phone_number = fake.msisdn()
    self.email = f"{self.name[0]}.{self.name.split(' ')[1:][0]}@{fake.domain_name()}".lower()

class Case:
  def __init__(self):
    self.case_id = fake.unique.random_number(digits=8)
    self.case_number = f"2023-39-INC-23{fake.random_number(digits=6)}"
    self.case_status_id = random.choice(list(status_vals.keys()))
    self.case_status = status_vals[self.case_status_id]
    self.police_department = random.choice(list(pd_vals.keys()))
    self.client_code = pd_vals[self.police_department]
    self.assignee = fake.first_name() + ' ' + fake.last_name() + ' ' + '('+str(fake.random_number(digits=4))+')'
    self.last_date_modified = str(fake.date_this_decade())
    self.last_modified_by = self.assignee
    self.number_of_victims = random.randrange(1, 4)
    self.case_type = random.choice(list(case_type))
    self.case_time = str(fake.date_this_decade())
    self.notification = True
    self.victim_names = None
    self.victim_emails = None
    self.victim_phone_numbers = None
    self.victim_id = None

  def gen_victim_info(self, number_of_victims):
    for _ in range(number_of_victims):
      _ = Victim()
      if self.victim_names is None:
        self.victim_names = _.name
      else:
        self.victim_names += ', ' + _.name
      if self.victim_phone_numbers is None:
        self.victim_phone_numbers = _.phone_number
      else:
        self.victim_phone_numbers += ', ' + _.phone_number
      if self.victim_emails is None:
        self.victim_emails = _.email
      else:
        self.victim_emails += ', ' + _.email
      if self.victim_id is None:
        self.victim_id = _.id
      else:
        self.victim_id += ', ' + _.id

# Not sure I need 'data_list' arg ?
async def load_cases_data(data_list):
  try:
    _ = Case()
    _.gen_victim_info(_.number_of_victims)

    values = {
      'case_id': _.case_id, 
      'case_number': _.case_number, 
      'case_status': _.case_status,
      'client_code': _.client_code, 
      'police_dpt': _.police_department, 
      'assignee': _.assignee,
      'last_date_modified': _.last_date_modified, 
      'last_modified_by': _.last_modified_by, 
      'victim_names': _.victim_names, 
      'victim_emails': _.victim_emails, 
      'case_status_id': _.case_status_id,
      'victim_phone_numbers': _.victim_phone_numbers, 
      'victim_ids': _.victim_id,
      'notification': _.notification, 
      'case_type': _.case_type, 
      'case_time': _.case_time
    }

    data_list.append(values)
  except Exception as e:
    print('Something went wrong: ', e)
    return

async def main():
  Supabase = Database()
  count = 25
  data_list = []
  try:
    while count > 0:
      async with asyncio.timeout(10):
        await load_cases_data(data_list)
        count -= 1
  except asyncio.TimeoutError:
    print('Job timed out')
    return
  except Exception as e:
    print('Unexpected error: ', e)
    return

  Supabase.client.table('cases_test_upload').insert(data_list).execute()
  print('Job complete')

asyncio.run(main())
