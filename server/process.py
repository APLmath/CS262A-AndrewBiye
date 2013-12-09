import cStringIO
import csv
import multiprocessing
import reorder
import shortuuid
import sqlalchemy

__ENGINE = sqlalchemy.create_engine('mysql://testuser:password@localhost/cs262a')
__METADATA = sqlalchemy.MetaData()
__UPLOADED_TABLES = sqlalchemy.Table('uploadedTables', __METADATA,
    autoload=True, autoload_with=__ENGINE)
__UPLOADED_TABLE_COLUMNS = sqlalchemy.Table('uploadedTableColumns', __METADATA,
    autoload=True, autoload_with=__ENGINE)

__CHUNK_SIZE = 10000

class BadTableIdException(Exception):
  pass

class BadIndexException(Exception):
  pass

# Convert a string to a number, if possible.
def to_number(s):
  try:
    return long(s)
  except:
    try:
      return float(s)
    except:
      return s

def __index_csv(args):
  table_id, i, j = args
  data_table = sqlalchemy.Table('table_' + table_id, __METADATA,
    autoload=True, autoload_with=__ENGINE)
  data = []
  data_select = sqlalchemy.select([
      data_table.c['id'],
      data_table.c['column' + str(i)],
      data_table.c['column' + str(j)]
  ])
  with __ENGINE.begin() as conn:
    data = list(conn.execute(data_select))
  ordering = reorder.reorder(data)
  data_update = data_table.update().where(
      data_table.c.id == sqlalchemy.bindparam('_id')).values(**{
        'index_' + str(i) + '_' + str(j): sqlalchemy.bindparam('_chunk')
      })
  with __ENGINE.begin() as conn:
    conn.execute(data_update, [{
      '_id': id,
      '_chunk': i / __CHUNK_SIZE
    } for i, id in enumerate(ordering)])

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

  number_columns = [i for i, column_name in enumerate(column_names)
      if column_name in number_type]
  index_pairs = []
  for i in range(len(number_columns) - 1):
    for j in range(i + 1, len(number_columns)):
      index_pairs.append((number_columns[i], number_columns[j]))

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
    for i, j in index_pairs:
      args.append(sqlalchemy.Column('index_' + str(i) + '_' + str(j),
          sqlalchemy.types.Integer))
    new_table = sqlalchemy.Table(*args)
    new_table.create(__ENGINE)

    conn.execute(new_table.insert(), [{
      synth_names[column_name]: value for column_name, value in row.iteritems()
    } for row in all_rows])

  pool = multiprocessing.Pool()
  pool.map_async(__index_csv, [(table_id, i, j) for i, j in index_pairs])

  return table_id

def get_chunk(table_id, index1, index2, chunk):
  columns_select = sqlalchemy.select([
    __UPLOADED_TABLE_COLUMNS.c.original_name,
    __UPLOADED_TABLE_COLUMNS.c.synth_name
  ]).where(__UPLOADED_TABLE_COLUMNS.c.table_id == table_id)
  data_table = sqlalchemy.Table('table_' + table_id, __METADATA,
    autoload=True, autoload_with=__ENGINE)
  original_names = {}
  synth_names = {}

  with __ENGINE.begin() as conn:
    for original_name, synth_name in conn.execute(columns_select):
      original_names[synth_name] = original_name
      synth_names[original_name] = synth_name
    csv_file = cStringIO.StringIO()
    writer = csv.DictWriter(csv_file, original_names.values())
    writer.writeheader()
    data_select = sqlalchemy.select(
        filter(lambda c: c[:6] == 'column', data_table.c))
    for row in conn.execute(data_select):
      writer.writerow({
        original_names[synth_name]: value for synth_name, value in row.items()
      })

  csv_file.seek(0)
  return csv_file
