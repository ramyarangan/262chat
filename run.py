#!venv/bin/python

'''
Launch the server at http://localhost:5000.
'''

from app import app
app.run(host='0.0.0.0',debug=True,port=5000)