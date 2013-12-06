import data
import webapp2
from google.appengine.ext.webapp import template

# Handler for the home page, with the upload form.
class HomeHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(template.render('templates/home.html', {}))

# Handler for the uploading itself.
class UploadHandler(webapp2.RequestHandler):
  def post(self):
    # Get the contents of the uploaded file.
    data_content = self.request.get('csv')

    # If empty, redirect back to the home page.
    if not data_content:
      self.redirect(self.uri_for('home'))

    filename = self.request.POST['csv'].filename

    # Otherwise, reflect it to the output.
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write(data_content)

# Handler to display the data for the given data ID in a nice way.
class ViewHandler(webapp2.RequestHandler):
  def get(self, data_id):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Hello, World! ' + str(data_id))

# Handler that returns the data in the desired chunks.
class DataHandler(webapp2.RequestHandler):
  def get(self, data_id):
    query_args = self.request.arguments()
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Hello, World! ' + str(query_args))

application = webapp2.WSGIApplication([
  webapp2.Route(r'/<data_id:\d+>', handler=ViewHandler, name='view'),
  webapp2.Route(r'/<data_id:\d+>/data', handler=DataHandler, name='data'),
  webapp2.Route(r'/upload', handler=UploadHandler),
  webapp2.Route(r'/', handler=HomeHandler, name='home'),
], debug=True)
