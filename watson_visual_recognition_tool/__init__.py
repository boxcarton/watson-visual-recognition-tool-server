from flask import Flask

app = Flask(__name__)

app.url_map.strict_slashes = False

import watson_visual_recognition_tool.controllers