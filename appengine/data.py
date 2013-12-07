import cStringIO
import csv
from google.appengine.ext import ndb



class Table(ndb.Model):
  # The original filename of the table.
  filename = ndb.StringProperty(required=True)
  # The list of the original names for all the columns in the table.
  original_columns = ndb.StringProperty(repeated=True)
  # The list of names for just the numerical columns.
  number_columns = ndb.StringProperty(repeated=True)

# Row will reproduce the values in the rows, albeit with synthesized field names.
class Row(ndb.Expando):
  pass


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

  
  table = Table(filename=filename, original_columns=reader.fieldnames)

  f.close()