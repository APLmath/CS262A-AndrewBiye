import bottle
import process

@bottle.route('/<table_id:re:[a-zA-Z0-9]{22}>')
def view(table_id):
  return 'View ' + str(table_id)

@bottle.route('/<table_id:re:[a-zA-Z0-9]{22}>/<index1>/<index2>/<chunk:int>')
def data(table_id, index1, index2, chunk):
  try:
    data = process.get_chunk(table_id, index1, index2, chunk)
    bottle.response.content_type = 'text/csv'
    return data
  except Exception:
    raise bottle.HTTPError(404)

@bottle.route('/static/<filename>')
def static(filename):
  return bottle.static_file(filename, root='./static')

@bottle.route('/upload', method='POST')
def upload():
  file_upload = bottle.request.files.get('csv')
  if file_upload:
    return process.save_csv(file_upload)
  else:
  	bottle.redirect('/')

@bottle.route('/')
@bottle.view('home')
def home():
  return {}

bottle.run(host='0.0.0.0', port=8080, debug=True)
