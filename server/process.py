import cStringIO
import csv
import multiprocessing
import reorder
import shortuuid
import sqlalchemy

__ENGINE = sqlalchemy.create_engine('mysql://testuser:password@localhost/cs262a')
__METADATA = sqlalchemy.MetaData()
__UPLOADED_TABLES = sqlalchemy.Table('uploaded_tables', __METADATA,
  sqlalchemy.Column('table_id', sqlalchemy.types.String(22), primary_key=True),
  sqlalchemy.Column('filename', sqlalchemy.types.String(256)),
  sqlalchemy.Column('num_chunks', sqlalchemy.types.Integer),
  sqlalchemy.Column('complete', sqlalchemy.types.Boolean))
__UPLOADED_TABLES.create(__ENGINE, checkfirst=True)
__UPLOADED_TABLE_COLUMNS = sqlalchemy.Table('uploaded_table_columns', __METADATA,
  sqlalchemy.Column('id', sqlalchemy.types.Integer, primary_key=True),
  sqlalchemy.Column('table_id', sqlalchemy.types.String(22),
      sqlalchemy.ForeignKey('uploaded_tables.table_id')),
  sqlalchemy.Column('original_name', sqlalchemy.types.String(256)),
  sqlalchemy.Column('synth_name', sqlalchemy.types.String(10)))
__UPLOADED_TABLE_COLUMNS.create(__ENGINE, checkfirst=True)

__CHUNK_SIZE = 10000

class BadTableIdException(Exception):
  pass

class BadIndexException(Exception):
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

# Records the uploaded CSV, and asynchronously fires off the CSV processing, so
# that it can return as quickly as possible.
def save_csv(file_upload):
  table_id = shortuuid.uuid()
  filename = file_upload.filename[:256]
  if not filename:
    raise Exception
  reader = csv.DictReader(file_upload.file)

  all_rows = list(reader)

  # Insert the record.
  with __ENGINE.begin() as conn:
    conn.execute(__UPLOADED_TABLES.insert(), {
      'table_id': table_id,
      'filename': filename,
      'num_chunks': (len(all_rows) - 1) / __CHUNK_SIZE + 1,
      'complete': False
    })
  
  # Kick off the heavy-duty processing separately.
  p = multiprocessing.Process(target=__process_csv, args=(table_id, all_rows))
  p.start()

  return table_id

# Populate the table and compute all of the chunk indices.
def __process_csv(table_id, all_rows):
  column_names = all_rows[0].keys()
  synth_names = {column_name: 'column' + str(i)
      for i, column_name in enumerate(column_names)}

  # Track which columns are purely numbers.
  number_type = {column: int for column in column_names}
  empty_columns = column_names[:]
  for row in all_rows:
    for number_column in number_type.keys():
      value = row[number_column]
      if not value:
        continue
      value = to_number(value)
      if type(value) is str:
        del number_type[number_column]
      elif type(value) is float:
        number_type[number_column] = float
    for column in empty_columns[:]:
      if row[column]:
        empty_columns.remove(column)
  for empty_column in empty_columns:
    del number_type[empty_column]

  # Find all the pairs of columns that may be used for indexing.
  number_columns = [i for i, column_name in enumerate(column_names)
      if column_name in number_type]
  index_pairs = []
  for i in range(len(number_columns) - 1):
    for j in range(i + 1, len(number_columns)):
      index_pairs.append((number_columns[i], number_columns[j]))

  # Re-synthesize the set of rows where the keys are renamed and the values are
  # typed accordingly.
  all_rows = [{
    synth_names[original_name]: (number_type[original_name](value)
        if original_name in number_type else value) if value else None
        for original_name, value in row.items()
  } for row in all_rows]

  # Kick off workers that each compute for a pair of indexing columns.
  pool = multiprocessing.Pool()
  # Dictionary to collect results.
  orderings = multiprocessing.Manager().dict()
  # Helper function to generate the arguments.
  def generate_reordering_args(index_pair):
    i, j = index_pair
    i = 'column' + str(i)
    j = 'column' + str(j)
    return (orderings, index_pair,
        [(index, row[i], row[j]) for index, row in enumerate(all_rows)
            if row[i] and row[j]])
  # Run the workers, and block until they finish.
  pool.map(__reorder, map(generate_reordering_args, index_pairs))

  # Add all the results to the rows.
  for (i, j), ordering in orderings.items():
    column_name = 'chunk_' + str(i) + '_' + str(j)
    for row in all_rows:
      row[column_name] = None
    for k, index in enumerate(ordering):
      all_rows[index][column_name] = k / __CHUNK_SIZE;

  # Set up a new table for the data.
  args = [
    'table_' + table_id, __METADATA,
    sqlalchemy.Column('id', sqlalchemy.types.Integer, primary_key=True)
  ]
  column_types = {
    float: sqlalchemy.types.Float,
    int: sqlalchemy.types.BigInteger,
    str: sqlalchemy.types.Text
  }
  for column_name in column_names:
    args.append(sqlalchemy.Column(synth_names[column_name], column_types[
        number_type[column_name] if column_name in number_type else str]))
  for i, j in index_pairs:
    args.append(sqlalchemy.Column('chunk_' + str(i) + '_' + str(j),
        sqlalchemy.types.Integer))
  new_table = sqlalchemy.Table(*args)

  # Finally, do all the MySQL commits!
  with __ENGINE.begin() as conn:
    # Record the column mappings.
    conn.execute(__UPLOADED_TABLE_COLUMNS.insert(), [{
        'table_id': table_id,
        'original_name': column_name,
        'synth_name': synth_names[column_name]
      } for column_name in column_names])
    # Create the new table for this data.
    new_table.create(__ENGINE)
    # Insert everything!
    conn.execute(new_table.insert(), all_rows)
    # Update the "completed" flag.
    conn.execute(__UPLOADED_TABLES.update().\
        where(__UPLOADED_TABLES.c.table_id == table_id).\
        values(complete=True))

# Effectively, this is not much more than a wrapper around the reordering
# function, for use by multiprocessing.
def __reorder(args):
  orderings, index_pair, data = args
  orderings[index_pair] = reorder.reorder(data)
  print index_pair, 'done!'

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
