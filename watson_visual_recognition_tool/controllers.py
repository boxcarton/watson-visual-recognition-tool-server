import os
from tempfile import TemporaryFile
from datetime import timedelta
from functools import update_wrapper

from flask import Flask, request, Response, g
from flask import render_template, url_for, send_from_directory
from flask import make_response, abort, jsonify

from watson_developer_cloud import VisualRecognitionV3
from watson_visual_recognition import WatsonVisualRecognition

from watson_visual_recognition_tool import app

my_vr = WatsonVisualRecognition()

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/api/classifiers', methods=['GET','OPTIONS'])
@crossdomain(origin='*')
def get_custom_classifiers():
  api_key = request.args.get('apiKey')
  classifiers = my_vr.list_classifiers(api_key)
  response = jsonify(classifiers)
  return response, response.status_code

@app.route('/api/classifier/<id>', methods=['GET','OPTIONS'])
@crossdomain(origin='*')
def get_custom_classifier_detail(id):
  api_key = request.args.get('apiKey')
  classifier = my_vr.get_classifier(id, api_key)
  response = jsonify(classifier)
  return response, response.status_code

@app.route('/api/classifiers', methods=['POST','OPTIONS'])
@crossdomain(origin='*')
def create_custom_classifier():
  classifier_name = request.form['classifier_name']
  api_key = request.form['api_key']

  files = {}

  for name, file in request.files.iteritems():
    tf = TemporaryFile()
    file.save(tf)
    tf.seek(0)

    if name == 'negative':
      files['negative_examples'] = tf
    else:
      files[name + '_positive_examples'] = tf

  new_classifier = my_vr.create_classifier(classifier_name, files, api_key)
  response = jsonify(new_classifier)
  
  return response, response.status_code

@app.route('/api/classify', methods=['POST','OPTIONS'])
@crossdomain(origin='*')
def classify_image():
  classifier_id = request.form['classifier_id']
  api_key = request.form['api_key']

  image_url = ''
  if 'image_url' in request.form:
    image_url = request.form['image_url']
  
  tf = None
  if request.files:
    tf = TemporaryFile()
    request.files['file'].save(tf)
    tf.seek(0)

  result = my_vr.classify_image(classifier_ids=classifier_id,
                                image_file=tf,
                                image_url=image_url,
                                threshold=0,
                                api_key=api_key)
  
  response = jsonify(result)
  
  return response, response.status_code

@app.route('/api/classifier/<id>', methods=['DELETE','OPTIONS'])
@crossdomain(origin='*')
def delete_custom_classifier(id):
  api_key = request.headers.get('apiKey')
  response = my_vr.delete_classifier(id, api_key)
  response = jsonify(response)
  return response, response.status_code

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@crossdomain(origin='*')
def index(**kwargs):
  return make_response(open('watson_visual_recognition_tool/templates/index.html').read())

# special file handlers and error handlers
@app.route('/favicon.ico')
@crossdomain(origin='*')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
         'img/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404