# DragEncrypt
DragEncrypt is the easiest way to encrypt a file that has ever existed. Drag and drag a file into a browser to encrypt or decrypt it - it's as simple as that. 

No software installation needed. No hard drive partitioning needed. 

Just an internet browser and an internet connection. 

## Setup
```
	virtualenv venv
	source venv\bin\activate
	pip install -r requirements.txt
```

## Dependencies
* Flask 
* Flask-login 
* Flask-SQLAlchemy 
* flask-bcrypt 
* pycrypto 
* gunicorn 
* mysql-python

## Running DragEncrypt
```
python server.py
```