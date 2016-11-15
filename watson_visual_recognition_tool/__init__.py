from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

import watson_visual_recognition_tool.controllers