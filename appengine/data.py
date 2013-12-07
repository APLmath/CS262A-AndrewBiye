import cStringIO
import csv
from google.appengine.ext import deferred
from google.appengine.ext import ndb

# Here, field names are actually mapped to synthesized field names to prevent
# collisions and such.

class Table(ndb.Model):
  # The original filename of the table.
  filename = ndb.StringProperty(required=True)
  # The list of the original names for all the fields in the table.
  field_names = ndb.StringProperty(repeated=True)
  # The list of names for just the numerical fields.
  number_fields = ndb.StringProperty(repeated=True)
  # Whether or not all the items have been written.
  all_items_written = ndb.BooleanProperty(default=False)

# Item will reproduce the values in a row.
class Item(ndb.Expando):
  pass

# Convert a string to a number, if possible.
def to_number(s):
  try:
    return int(s)
  except:
    try:
      return float(s)
    except:
      return s

def save_csv(filename, contents):
  f = cStringIO.StringIO(contents)
  reader = csv.DictReader(f)
  field_names = reader.fieldnames
  all_rows = list(reader)[:1000]
  f.close()

  # Determine which fields contain only numerical values
  number_fields = field_names[:]
  for row in all_rows:
    for field in number_fields[:]:
      value = row[field]
      if value and type(to_number(value)) is str:
        number_fields.remove(field)

  table = Table(filename=filename,
                field_names=field_names,
                number_fields=number_fields)
  table.put()

  deferred.defer(deferred_save_rows, table, all_rows)

  return table.key.integer_id()

def deferred_save_rows(table, all_rows):
  field_names = table.field_names
  number_fields = table.number_fields
  items = []
  for row in all_rows:
    item = Item(parent=table.key)
    item._properties = {
      'field' + str(i):
        ndb.GenericProperty('field' + str(i), indexed=True)
        if field in number_fields else
        ndb.TextProperty('field' + str(i))
      for i, field in enumerate(field_names) if row[field]
    }
    item._values = {
      'field' + str(i):
        to_number(row[field]) if field in number_fields else row[field]
      for i, field in enumerate(field_names) if row[field]
    }
    items.append(item)
  ndb.put_multi(items)
  table.all_items_written = True
  table.put()

def get_csv(data_id):
  table_key = ndb.Key(Table, data_id)
  item_query = Item.query(ancestor=table_key)

  table = table_key.get()
  ret = table.filename
  if table.all_items_written:
    for item in item_query:
      ret += '\n' + str(getattr(item, 'field0'))
  else:
    ret += '\nNot done processing...'
  return ret
