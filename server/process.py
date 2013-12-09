import csv
import shortuuid
import sqlalchemy

__ENGINE = sqlalchemy.create_engine('mysql://testuser:password@localhost/cs262a')
__METADATA = sqlalchemy.MetaData()
__UPLOADED_TABLES = sqlalchemy.Table('uploadedTables', __METADATA,
    autoload=True, autoload_with=__ENGINE)
__UPLOADED_TABLE_COLUMNS = sqlalchemy.Table('uploadedTableColumns', __METADATA,
    autoload=True, autoload_with=__ENGINE)

# Convert a string to a number, if possible.
def to_number(s):
  try:
    return long(s)
  except:
    try:
      return float(s)
    except:
      return s

def save_csv(file_upload):
  table_id = shortuuid.uuid()
  filename = file_upload.filename[:256]
  if not filename:
    raise Exception
  reader = csv.DictReader(file_upload.file)
  column_names = [column_name[:256] for column_name in reader.fieldnames]
  synth_names = {column_name: 'column' + str(i) for i, column_name in enumerate(column_names)}
  # Dict tracking the number types.
  number_type = {column: long for column in column_names}

  all_rows = []
  for row in reader:
    for number_column in number_type.keys():
      value = to_number(row[number_column])
      if type(value) is str:
        del number_type[number_column]
      elif type(value) is float:
        number_type[number_column] = float
    all_rows.append(row)
  for row in all_rows:
    for number_column in number_type:
      row[number_column] = number_type[number_column](row[number_column])

  with __ENGINE.begin() as conn:
    conn.execute(__UPLOADED_TABLES.insert(), {
      'table_id': table_id,
      'filename': filename
    })
    conn.execute(__UPLOADED_TABLE_COLUMNS.insert(), [{
        'table_id': table_id,
        'original_name': column_name,
        'synth_name': synth_names[column_name]
      } for column_name in column_names])

    args = ['table_' + table_id, __METADATA,
        sqlalchemy.Column('id', sqlalchemy.types.Integer, primary_key=True)]
    for column_name in column_names:
      column_type = (sqlalchemy.types.BigInteger if number_type[column_name] is long
          else sqlalchemy.types.Float) if column_name in number_type else sqlalchemy.types.Text
      args.append(sqlalchemy.Column(synth_names[column_name], column_type))
    new_table = sqlalchemy.Table(*args)
    new_table.create(__ENGINE)

    conn.execute(new_table.insert(), [{
      synth_names[column_name]: value for column_name, value in row.iteritems()
    } for row in all_rows])
  return table_id
