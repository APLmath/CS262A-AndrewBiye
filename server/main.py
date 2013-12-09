import bottle
import process

@bottle.route('/<data_id:re:[a-zA-Z0-9]{22}>')
def view(data_id):
  return 'View ' + str(data_id)

@bottle.route('/<data_id:re:[a-zA-Z0-9]{22}>/data')
def data(data_id):
  return 'Data ' + str(data_id)

@bottle.route('/static/<filename>')
def static(filename):
  return bottle.static_file(filename, root='./static')

@bottle.route('/upload', method='POST')
def upload():
  file_upload = bottle.request.files.get('csv')
  if file_upload:
    return file_upload.file.read()
  else:
  	bottle.redirect('/')

@bottle.route('/')
@bottle.view('home')
def home():
  return {}

bottle.run(host='0.0.0.0', port=8080, debug=True)
