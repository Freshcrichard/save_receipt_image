import os
from refreshbooks import api
import time
from datetime import datetime
from datetime import date

#account URL, API Token, and date range applied in these fields
url = ''
token = ''
date_from = datetime.strptime('01/01/14', '%m/%d/%y')
date_to = datetime.today()

def main_program():
    api_caller = api.TokenClient(url, token)
    receipts = []
    date = {}
    count = 1
    #Build a list of expense_ids
    expenses = list_all(api_caller.expense.list, 'expense')
    for expense in expenses:
        #Estabilsh the date in datetime format for an expense, accounting for exceptions
        datevar = get_datevar(expense.date)
        #Go through all expenses, check if they are within the date range and have a receipt.  If so, append to list.
        if expense.has_receipt == 1:
            if datecheck(datevar):
                receipts.append(expense.expense_id)
                #create a dictionary of ExpenseID:Date structure. Used for naming image files below.
                date[expense.expense_id] = str(expense.date)[0:10]

    #create a directory to dump the files, move into that directory
    ensure_dir('/users/crichard/desktop/python_practice/'+url+'_receipts/')

    #capture receipt file
    for receipt_id in receipts:
        print count
        header, body = api_caller.receipt.get(expense_id=int(receipt_id))
        #check file type
        extension = get_file_type_extension(header)
        count = count + 1
        #write the image file to the current directory
        with open(ensure_file("%s-%s.%s" % (url, date[receipt_id], extension),date[receipt_id], extension), 'wb') as f:
          f.write(body)
        if count % 50 == 0:
          time.sleep(1)

def list_all(command, entity):
    page = 1
    per_page = 100
    last_page = False

    while last_page is False:
        try:
            response = command(page=str(page), per_page=str(per_page))
            entities = getattr(response, pluralize(entity))
            for item in getattr(entities, entity):
                yield item
            last_page = entities.attrib['page'] == entities.attrib['pages']
        finally:
            page += 1


def pluralize(entity):
    return entity + 's'

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
    os.chdir(d)

def ensure_file(f,d, e):
    tag = 1
    while os.path.isfile(f):
      f = "%s-%s #%s.%s" % (url, d, str(tag), e)
      tag = tag + 1
    return f

def get_file_type_extension(h):
    if h['content-type'] == 'image/jpeg;':
      extension = 'jpg'
    elif h['content-type'] == 'image/gif;':
      extension = 'gif'
    elif h['content-type'] == 'image/png;':
      extension = 'png'
    elif h['content-type'] == 'application/pdf;':
      extension = 'pdf'
    return extension

def get_datevar(date_in):
    try:
        return datetime.strptime(str(date_in)[2:10], '%y-%d-%m')
    except ValueError, v:
        ulr = len(v.args[0].partition('unconverted data remains: ')[2])
        if ulr:
            return datetime.strptime(str(date_in)[2:10-ulr], '%y-%d-%m')
        else:
            raise v

def datecheck(date):
    if date >= date_from:
      if date <= date_to:
        return True
    else:
      return False

main_program()
