import os
from dotenv import load_dotenv, find_dotenv
from pprint import pprint
from watson_developer_cloud import VisualRecognitionV3
import json
import requests
import tempfile

class WatsonVisualRecognition:

  end_point = "https://gateway-a.watsonplatform.net/visual-recognition/api"
  latest_version = '2016-05-20'
  
  def __init__(self, api_key, end_point=end_point, version=latest_version):
    self.api_key = api_key
    self.end_point = end_point
    self.version = version

  def list_classifiers(self):
    url = '/v3/classifiers'
    params = {'api_key': self.api_key, 'version': self.version}

    return requests.get(self.end_point + url, 
                        params=params).json()['classifiers']

  def get_classifier(self, classifier_id):
    url = '/v3/classifiers' + '/' + classifier_id
    params = {'api_key': self.api_key, 'version': self.version}

    return requests.get(self.end_point + url,
                        params=params).json()

  def create_classifier(self, classifier_name, class_files):
    url = '/v3/classifiers'
    params = {'api_key': self.api_key, 'version': self.version}

    files = {
      'name': (None, classifier_name)
    }

    for class_name, file in class_files.iteritems():
      files[class_name] = (class_name + ".zip",
                           file,
                           'application/zip')

    return requests.post(self.end_point + url,
                         files=files,
                         params=params,
                        ).json()

  def delete_classifier(self, classifier_id):
    url = '/v3/classifiers/' + classifier_id
    params = {'api_key': self.api_key, 'version': self.version}
    response = requests.delete(self.end_point + url,
                           params=params).json()
    return requests.delete(self.end_point + url,
                           params=params).json()

  def delete_all_classifiers(self):
    responses = []
    for classifier in self.list_classifiers():
      r = self.delete_classifier(classifier['classifier_id'])
      responses.append(r)

    return responses

  def classify_image(self, classifier_ids, image_file=None, image_url="", threshold=0):
    url = '/v3/classify'
    params = {'api_key': self.api_key, 'version': self.version}

    if isinstance(classifier_ids, str) or isinstance(classifier_ids, unicode):
      classifier_ids = [classifier_ids]
    else:
      if not isinstance(classifier_ids, list):
        raise TypeError("classifier_ids needs to be either string or list.")

    parameters = {
      'classifier_ids': classifier_ids,
      'threshold': threshold,
      'url': image_url
    }

    files = {
      'parameters': (None, json.dumps(parameters)),
    }

    if image_file:
      files['images_file'] = (None, image_file, 'image/jpg')

    return requests.post(self.end_point + url,
                         files=files,
                         params=params).json()

def main():
  #load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
  load_dotenv(find_dotenv())
  api_key=os.environ.get("API_KEY")

  #visual_recognition = WatsonVisualRecognition(api_key)

  sdk_vr = VisualRecognitionV3('2016-05-20', api_key=api_key)
  my_vr = WatsonVisualRecognition(api_key)
  
  ''' 
  image_path = '/Users/joshuazheng/Downloads/Beagle_hero.jpg'
  image_file = open('/Users/joshuazheng/Downloads/Beagle_hero.jpg').read()
  image_url = 'http://www.sbarro.com/wp-content/uploads/2015/04/12-sbarro-spaghetti-meatballs.jpg'
  classifier_id = 'dogs_2117373684'
  pprint(my_vr.classify_image(classifier_id, image_file=None, image_url=image_url, threshold=0))
  
   
  pos_file_paths = ['bundles/moleskine/journaling.zip', 'bundles/moleskine/journaling.zip']
  neg_file_path = 'bundles/moleskine/negative.zip'
  pos_file_list = [journal, land]
  pos_files = {'journ': journal, 'land': land}
  pos_names = ['journal', 'land']
  

  files = {
    'negative_examples': open('../bundles/moleskine/negative.zip').read(),
    'journal_positive_examples': open('../bundles/moleskine/journaling.zip').read(),
    'landscape_positive_examples': open('../bundles/moleskine/journaling.zip').read()
  }

  response = my_vr.create_classifier("mol_script_zipnew", files)
  #response = my_vr.create_classifier_from_file("mol_script_file1", pos_names, pos_file_list, neg_file_path)
  #import pdb; pdb.set_trace()
  print response
  print(sdk_vr.get_classifier('beagle_81816899'))
  print
  print "SDK"
  classes = my_vr.list_classifiers()
  pprint(classes)
  print
  print
  for c in classes:
    info = sdk_vr.get_classifier(c['classifier_id'])
    pprint(info)
    print
  '''

  print my_vr.get_classifier('piz_525944347')
  

if __name__ == "__main__":
    main()