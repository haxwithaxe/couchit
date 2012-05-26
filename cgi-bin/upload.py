#!/usr/bin/env python

import cgi
import os
import sys
import json

DEBUG=True
if DEBUG: import cgitb;cgitb.enable()
FILE_FIELDS=[{'name':'file1'}]
UPLOADDIR='../uploads'

def grab_file(form_field,upload_dir = UPLOADDIR):
	form = cgi.FieldStorage()
	if not form.has_key(form_field): return False
	fileitem = form[form_field]
	if not fileitem.file: return False
	fout = file (os.path.join(upload_dir, fileitem.filename), 'wb')
	while 1:
		chunk = fileitem.file.read(100000)
		if not chunk: break
		fout.write (chunk)
	fout.close()
	return True

if __name__ == '__main__':
	jsondict = {}
	print('Content-Type: text/plain\n\n')
	for f in FILE_FIELDS:
		if 'dest' in f:
			stat = grab_file(f['name'],f['dest'])
		else:
			stat = grab_file(f['name'])
		if stat:
			jsondict.update({f['name']:'OK'})
		else:
			jsondict.update({f['name']:'FAILED'})
	print(json.dumps(jsondict))



