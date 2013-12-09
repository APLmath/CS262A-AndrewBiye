<!DOCTYPE html>
<meta charset="utf-8">
<link rel="stylesheet" type="text/css" href="static/style.css">
<title>Scattr</title>

<h1>Scattr</h1>

<form enctype="multipart/form-data" action="/upload" method="post">
  <h3>Select a <code>.CSV</code> file to upload:</h3>
  <input name="csv" type="file" accept=".csv" /><input type="submit" value="Upload" />
</form>
