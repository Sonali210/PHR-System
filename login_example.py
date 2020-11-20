from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory
from flask_pymongo import PyMongo
import bcrypt
from flask import Flask, Response
import webbrowser
import os
import cv2
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
lst = ['Malignant','Beningn','no skin ']
np.set_printoptions(suppress=True)

import requests
from flask import Flask,render_template
URL = "https://discover.search.hereapi.com/v1/discover"
latitude = 12.96643
longitude = 77.5871
api_key = '1idGsC3uqoA3MwN0NfyNVlSOqSxpD96MeFZh2zSB8fE' # Acquire from developer.here.com
query = 'Skin Cancer hospital'
limit = 5

PARAMS = {
            'apikey':api_key,
            'q':query,
            'limit': limit,
            'at':'{},{}'.format(latitude,longitude)
         } 

# sending get request and saving the response as response object 
r = requests.get(url = URL, params = PARAMS) 
data = r.json()
print(data['items'][0]['categories'][0]['name'])

hospitalOne = data['items'][0]['title']
hospitalOne_address =  data['items'][0]['address']['label']
hospitalOne_latitude = data['items'][0]['position']['lat']
hospitalOne_longitude = data['items'][0]['position']['lng']
hospitalOne_contect = data['items'][0]['contacts'][0]['mobile'][0]['value']
hospitalOne_distance = data['items'][0]['distance']
hospitalOne_Docter_name = data['items'][0]['categories'][0]['name']

hospitalTwo = data['items'][1]['title']
hospitalTwo_address =  data['items'][1]['address']['label']
hospitalTwo_latitude = data['items'][1]['position']['lat']
hospitalTwo_longitude = data['items'][1]['position']['lng']

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config['MONGO_DBNAME'] = 'user'
# app.config['MONGO_URI'] = 'mongodb://pretty:printed@ds021731.mlab.com:21731/mongologinexample'
app.config['MONGO_URI']= 'mongodb+srv://user:user987@cluster0.b50jf.mongodb.net/user?retryWrites=true&w=majority'

mongo = PyMongo(app)

@app.route('/')
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']
    else:
        return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    else:
        return render_template('upload.html')

    return 'Invalid username/password combination'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'
    else:
        return render_template('register.html')
@app.route("/home")
def home():
    return render_template("upload.html")    
@app.route("/upload", methods=["POST"])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    print(target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accept incoming file:", filename)
        print ("Save it to:", destination)
        upload.save(destination)
    # Load the model
    model = tensorflow.keras.models.load_model('keras_model.h5',compile=False)
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # Replace this with the path to your image
    folder='images'
    ex=folder+'/'+filename
    image = Image.open(ex)
    img=cv2.imread(ex)
    img = cv2.resize(img, (0, 0), fx = 0.2, fy = 0.2)

    #resize the image to a 224x224 with the same strategy as in TM2:
    #resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    #turn the image into a numpy array
    image_array = np.asarray(image)
    if len(image_array.shape) == 2: # ----------------Change here
        image_array.resize(224, 224, 1)

    # display the resized image
    #image.show()

    #cv2_imshow(img)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Load the image into the array
    data[0] = normalized_image_array 

    # run the inference
    prediction = model.predict(data)
    #print(type(prediction))
    prediction = list(prediction)

    print(prediction)
    # print(prediction[0][0])
    # print(prediction[0][1])
    class1=round(prediction[0][0]*100,2)
    class2=round(prediction[0][1]*100,2)
    class3=round(prediction[0][2]*100,2)
    print(class1,class2,class3)
    return render_template("complete_display_image.html",image_name=filename,class1=class1,class2=class2,class3=class3)
    #print(type(prediction))

    #if (prediction[0][0]>prediction[0][1]):
      #pred=prediction[0][0]*100
      #return render_template("complete_display_image.html", image_name=filename, prediction=pred)

    #else:
      #pred=prediction
      #return render_template("complete_display_image.html", image_name=filename, prediction=lst[1])

@app.route('/location')
def location():
	return render_template('map.html',
                            latitude = latitude,
                            longitude = longitude,
                            apikey=api_key,
                            oneName=hospitalOne,
                            OneAddress=hospitalOne_address,
                            OneDocterName=hospitalOne_Docter_name,
                            OneContect=hospitalOne_contect,
                            OneDistance=hospitalOne_distance,
                            oneLatitude=hospitalOne_latitude,
                            oneLongitude=hospitalOne_longitude,
                            twoName=hospitalTwo,
                            twoAddress=hospitalTwo_address,
                            twoLatitude=hospitalTwo_latitude,
                            twoLongitude=hospitalTwo_longitude,
                            )
    
@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=2205, debug=True)