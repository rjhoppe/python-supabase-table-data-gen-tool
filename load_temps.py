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

pd_vals = {'Peddleton PD': '37591', 'Acadia PD': '27402', ' Snowview PD': '29470', 'Goldburgh PD': '02749',
           'Casterley PD': '13754', 'North Lexington PD': '83242', 'Hardford PD': '24213', 'Lakegaard PD': '26183', 
           'Rosefolke PD': '14163','Greenhove PD': '35416', 'Springhoff PD': '23432', 'Blackwood PD': '48282', 
           'Canyon Valley PD': '12352'}

class Database:
  def __init__(self):
    self.url = os.getenv("SUPA_PROJECT_URL")
    self.key = os.getenv("SUPA_SERVICE_ROLE")
    self.client = create_client(self.url, self.key)

  async def load_temp_data(self, data_list, i):
    try:
      # print(data_list[0]['temp_table_vals'])
      self.client.table('templates').insert(data_list[i]['temp_table_vals']).execute()
    except Exception as e:
      print(e)

  async def load_rule_data(self, data_list, i):
    try:
      print(data_list[0]['rule_table_vals'])
      self.client.table('rules').insert(data_list[i]['rule_table_vals']).execute()
    except Exception as e:
      print(e)

class Template:
  def __init__(self) -> None:
    self.temp_id = str("T"+ str(fake.unique.random_number(digits=7)))
    self.police_department = random.choice(list(pd_vals.keys()))
    self.client_code = pd_vals[self.police_department]
    self.type = random.choice(['SMS', 'Email'])
    self.temp_created_by = fake.first_name() + ' ' + fake.last_name() + ' ' + '('+str(fake.random_number(digits=4))+')'
    self.temp_gen_creation_date = fake.date_this_decade()
    self.temp_creation_date = str(self.temp_gen_creation_date)
    self.temp_last_modified_by_other = fake.first_name() + ' ' + fake.last_name() + ' ' + '('+str(fake.random_number(digits=4))+')'
    self.temp_last_modified_by = random.choice([self.temp_created_by, fake.first_name() + ' ' + fake.last_name() + ' ' + '('+str(fake.random_number(digits=4))+')'])
    self.temp_last_date_modified = str(fake.date_between(self.temp_gen_creation_date))
    self.temp_cc_recipients = self.temp_last_modified_by
    self.temp_subject = 'An Update on Your Case Status'
    self.temp_active = random.choice(['True', 'False'])
    
    self.rule_id = str("R"+ str(fake.unique.random_number(digits=7)))
    self.rule_last_modified_by = random.choice([self.temp_created_by, fake.first_name() + ' ' + fake.last_name() + ' ' + '('+str(fake.random_number(digits=4))+')'])
    self.rule_last_date_modified = str(fake.date_between(self.temp_gen_creation_date))
    self.rule_delay = random.choice(['1 Hour', '3 Hours', '12 Hours', '24 Hours'])
    self.rule_status = random.choice(['Active', 'Investigator Assigned', 'Court Scheduled', 'Rejected', 'Closed'])
    self.rule_if = str('Status set to ' + self.rule_status)

    self.temp_name = str(self.rule_status + ' ' + '(' + self.type + ')')
    self.temp_message_content = f'Your case status has been updated to {self.rule_status}. ' + \
    f'Please visit www.{self.police_department.lower()}.org for more information'
    self.rule_then = str('Send ' + self.type + ' to victims in case using ' + self.temp_name)
    
async def gen_data(data_list):
  try:
    _ = Template()
    nested_data = {
      'temp_table_vals' : {
        'template_id': _.temp_id,
        'template_name': _.temp_name,
        'police_dpt': _.police_department,
        'client_code': _.client_code,
        'type': _.type,
        'created_by': _.temp_created_by,
        'last_date_modified': _.temp_last_date_modified,
        'last_modified_by': _.temp_last_modified_by,
        'cc_recipients': _.temp_cc_recipients,
        'active': _.temp_active,
        'subject': _.temp_subject, # Make Null in db
        'message': _.temp_message_content
      },  
      'rule_table_vals' : {
        'rule_id': _.rule_id,
        'police_dpt': _.police_department,
        'client_code': _.client_code,
        'created_by': _.temp_created_by,
        'last_date_modified': _.rule_last_date_modified,
        'last_modified_by': _.rule_last_modified_by,
        'delay': _.rule_delay,
        'status': _.rule_status,
        'if_logic': _.rule_if,
        'then_logic': _.rule_then
      }
    }
    data_list.append(nested_data)

  except Exception as e:
    print('Something went wrong: ', e)
    return
  
async def main():
  Supabase = Database()
  count = 50
  data_list = []
  try:
    while count > 0:   
      async with asyncio.timeout(10):
        await gen_data(data_list)
        count -= 1
    for i in range(len(data_list)):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(Supabase.load_temp_data(data_list, i))
        tg.create_task(Supabase.load_rule_data(data_list, i))
  except asyncio.TimeoutError:
    print('Job timed out')
    return
  except Exception as e:
    print('Unexpected error: ', e)
    return

  print('Job complete')

asyncio.run(main())

