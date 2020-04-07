import flask
from flask import request, jsonify
from flask import render_template
import main
from main import *


if __name__ == '__main__':
    
    #sending requests for fetching data 
    session_requests()

    app = flask.Flask(__name__,static_folder='static')
    

    
    @app.route('/', methods=['GET'])
    def home():    
        return render_template('index.html')
    
    
    app.run(debug=False)
    
    


    
    