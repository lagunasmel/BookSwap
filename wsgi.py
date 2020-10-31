"""
Module for WSGI, which is middleware: serving Flask (a Python module) to the 
web server.  You can ignore this file if you like, and just test at home by 
typing:
    python3 app.py
"""

from app import app

if __name__ == "__main__":
    app.run()
    
