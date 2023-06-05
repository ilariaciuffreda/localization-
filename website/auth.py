from unicodedata import category, name
from cv2 import distanceTransform
from flask import Blueprint, render_template, request, flash, redirect, send_file,url_for,jsonify
from flask_restful import Resource, Api, reqparse
import flask 
from .models import User 
from . import db
import ast 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import requests
import cv2 
import io
from PIL import Image
import base64
from pynput.mouse import Listener
from pynput.mouse import Controller
import yaml
from pynput import mouse 
from tkinter import *
import time 
import numpy as np
import matplotlib.pyplot as plt
import random, copy
import mysql.connector 
import datetime
import json
from flask_restful import Resource, Api
import os 
import pickle 
import math
import pandas as pd
def getConnection():
    mydb = mysql.connector.connect ( 
    host = "localhost", 
    user = "root", 
    password = "Ilaria1996.", 
    database= "localization"
    
    )

    return mydb 

mydb = getConnection()
mycursor = mydb.cursor()
print(mydb)

model = pickle.load(open("model.plk","rb"))    
direzionex= []
direzioney = [] 

auth = Blueprint('auth', __name__)


@auth.route ('/login', methods = ['POST','GET'])   
def login(): 
   if request.method == 'POST': 
       email = request.form.get('email')
       password = request.form.get ('password')
    
       user = User.query.filter_by(email = email).first()
       if user: 
           if check_password_hash (user.password, password): 
               
               flash ('logged in successfully!', category= 'success')
               login_user(user, remember=True)
               mycursor.execute("SELECT name FROM map" ) 
               name = mycursor.fetchall()   
               mycursor.execute("SELECT image FROM map" )  
               image  = mycursor.fetchall()
               #data = (io.BytesIO(image[0][0]))
               data = base64.b64encode(image[0][0])
               data = (data.decode( "UTF-8"))

              
               return render_template("login.html")
               
       else: 
            flash ('Email does not exist.', category='error') 
    
   return render_template("login.html")



@auth.route ('/', methods = ['POST','GET'])
def home(): 
   if request.method == 'POST': 
       flash ('IP address correctly saved', category='success') 
       IPaddress = request.form.get('IP address')
       slam = requests.get('http://'+ IPaddress +'/api/slam')
       slam = slam.json()
       slam= slam.get ('result')
       grid = slam.get('grid')
       print (len(grid))
       if len(grid) == 0:
           flash ('Please wait.. I am downloading the map of your home!') 
           getcurrentmap = requests.get('http://'+  IPaddress + '/api/slam/map/current')
           getcurrentmap = getcurrentmap.json()
           result = getcurrentmap.get('result')
           result = result [:-4]
           mycursor.execute("SELECT name FROM map WHERE name IS NOT NULL" )  
           print(mycursor)
           name  = mycursor.fetchall()
           name = name [-1]
           mycursor.execute("SELECT image FROM map WHERE image IS NOT NULL" )  
           print(mycursor)
           image  = mycursor.fetchall()
           image = image [-1]
       else :   
           flash ('Please wait.. I am downloading the map of your home!') 
           height = slam.get('height')
           grid = slam.get('grid')
           width = slam.get('width')
           img = np.reshape(grid,(height,width)).astype(float)
           meterspercells = slam.get('metersPerCell')
           originX = slam.get('originX')
           originX1 = 0-(originX / meterspercells) 
           originY = slam.get('originY')
           originY1 = 0-(originY / meterspercells)
           originX1 = round(originX) #dove ha iniziato a mappare ( coordinata x)
           originY1 = round(originY) #dove ha iniziato a mappare ( coordinata y)
           posex = originX1
           posey = originY1
           getcurrentmap = requests.get('http://'+ IPaddress + '/api/slam/map/current')
           getcurrentmap = getcurrentmap.json()
           result = getcurrentmap.get('result')
           result = result [:-4]   
           grid = "".join([str(elem) for elem in grid])
           mycursor.execute('INSERT INTO map(height) VALUES (%s)', height)
           mycursor.execute('INSERT INTO map(image) VALUES (%s)', (grid,))
           mycursor.execute('INSERT INTO map(width) VALUES (%s)', (width,))
           mycursor.execute('INSERT INTO map(posex) VALUES (%s)', (posex,))
           mycursor.execute('INSERT INTO map(posey) VALUES (%s)', (posey,))
           mycursor.execute('INSERT INTO map(meterspercell) VALUES (%s)', (meterspercells,))
           mydb.commit()
   return redirect ("/")  

@auth.route ('/map')

def map():
      flash ('Please wait.. I am downloading the map of your home!') 
      mycursor.execute("SELECT image FROM map WHERE image IS NOT NULL" )  
      print(mycursor)
      image = mycursor.fetchall()
      image = image[-1] #in realtà è -1, ma le immagini costruite fanno schifo. 
      
      #image.save(image, "JPEG")
      image_map = image[0].decode( "UTF-8")
    
      #print(image_map)  
      return render_template("map.html", image_map = image_map)  

 
@auth.route ('/createmap',methods = ['POST','GET'])
def createmap():
    mycursor.execute("SELECT Kitchen FROM map WHERE Kitchen IS NOT NULL" )  
    print(mycursor)
    Kitchen_coordinates  = mycursor.fetchall()
    mycursor.execute("SELECT Bathroom FROM map WHERE Bathroom IS NOT NULL" )  
    print(mycursor)
    Bathroom_coordinates  = mycursor.fetchall()
    mycursor.execute("SELECT LivingRoom FROM map WHERE LivingRoom IS NOT NULL" )  
    print(mycursor)
    LivingRoom_coordinates  = mycursor.fetchall()
    mycursor.execute("SELECT Bedroom FROM map WHERE Bedroom IS NOT NULL" )  
    print(mycursor)
    Bedroom_coordinates  = mycursor.fetchall()
    Kitchen_coordinates = Kitchen_coordinates[-1]
    Kitchen_coordinates = Kitchen_coordinates[0]
    Kitchen_coordinates = Kitchen_coordinates.replace('[', '')
    Kitchen_coordinates = Kitchen_coordinates.replace(']','')
    Kitchen_coordinates = Kitchen_coordinates.split(',')
    Kitchen_coordinates = np.asarray([int(x) for x in Kitchen_coordinates])
    Kitchen_coordinates = Kitchen_coordinates.reshape (int(len(Kitchen_coordinates)/2),-1)
    Bathroom_coordinates = Bathroom_coordinates[-1]
    Bathroom_coordinates = Bathroom_coordinates[0]
    Bathroom_coordinates = Bathroom_coordinates.replace('[', '')
    Bathroom_coordinates = Bathroom_coordinates.replace(']','')
    Bathroom_coordinates = Bathroom_coordinates.split(',')
    Bathroom_coordinates = np.asarray([int(x) for x in Bathroom_coordinates])
    Bathroom_coordinates = Bathroom_coordinates.reshape (int(len(Bathroom_coordinates)/2),-1)
    LivingRoom_coordinates = LivingRoom_coordinates[-1]
    LivingRoom_coordinates = LivingRoom_coordinates[0]
    LivingRoom_coordinates = LivingRoom_coordinates.replace('[', '')
    LivingRoom_coordinates = LivingRoom_coordinates.replace(']','')
    LivingRoom_coordinates = LivingRoom_coordinates.split(',')
    LivingRoom_coordinates = np.asarray([int(x) for x in LivingRoom_coordinates])
    LivingRoom_coordinates = LivingRoom_coordinates.reshape (int(len(LivingRoom_coordinates)/2),-1)
    Bedroom_coordinates =  Bedroom_coordinates[-1]
    Bedroom_coordinates =  Bedroom_coordinates[0]
    Bedroom_coordinates =  Bedroom_coordinates.replace('[', '')
    Bedroom_coordinates =  Bedroom_coordinates.replace(']','')
    Bedroom_coordinates =  Bedroom_coordinates.split(',')
    Bedroom_coordinates = np.asarray([int(x) for x in  Bedroom_coordinates])
    Bedroom_coordinates =  Bedroom_coordinates.reshape (int(len(Bedroom_coordinates)/2),-1)
    mycursor.execute("SELECT image FROM map WHERE image IS NOT NULL" )  
    print(mycursor)
    image_return  = mycursor.fetchall()

    for x in image_return:
    # Convert the image to a numpy array
        image = np.asarray(bytearray(x[0]), dtype="uint8")
    # Decode the image to a cv2 image
        s = cv2.imdecode(image, cv2.IMREAD_COLOR)
    # Convert the image from cv2's BGR to RGB that matplotlib expects
        s = cv2.cvtColor(s, cv2.COLOR_BGR2RGB)
        resized_image = cv2.resize(s, (1024, 768))
        isClosed = True
        color = (255, 0, 0)
        thickness = 2

        image = cv2.polylines(resized_image, [Kitchen_coordinates], 
                      isClosed, color, thickness)
        image = cv2.polylines(resized_image, [Bathroom_coordinates], 
                      isClosed, color, thickness)
        image = cv2.polylines(resized_image, [LivingRoom_coordinates], 
                      isClosed, color, thickness)
        image = cv2.polylines(resized_image, [Bedroom_coordinates], 
                      isClosed, color, thickness)              
    plt.imshow(image)
    plt.show()
    return render_template("createmap.html")
    
        

@auth.route ('/Kitchen',methods = ['POST','GET']) 
def Kitchen ():
    mycursor = mydb.cursor()
    print ( mycursor)
    if request.method == 'POST':
        points = request.get_json()
        print (points)
        points =  ("".join([str(elem) for elem in points]))
        print(points)
    try:
        mycursor.execute('INSERT INTO map(Kitchen) VALUES (%s)', (points,))
        print ( mycursor)
        mydb.commit()
        mycursor.close()
        print('data successfully inserted ')
        return redirect ('/map')       
    except:
        print("An error has occured")        
    return redirect('/map')

@auth.route ('/Bathroom',methods = ['POST','GET']) 
def Bathroom ():
    mycursor = mydb.cursor()
    print ( mycursor)
    if request.method == 'POST': 
        points = request.get_json()
        print (points)
        points =  ("".join([str(elem) for elem in points]))
        print(points)
    try:
        mycursor.execute('INSERT INTO map(Bathroom) VALUES (%s)', (points,))
        print ( mycursor)
        mydb.commit()
        mycursor.close()
        print('data successfully inserted ')
        return redirect ('/map')       
    except:
        print("An error has occured")        
    return redirect('/map')

@auth.route ('/LivingRoom',methods = ['POST','GET']) 
def LivingRoom ():
    mycursor = mydb.cursor()
    print ( mycursor)
    if request.method == 'POST': 
        points = request.get_json()
        print (points)
        points =  ("".join([str(elem) for elem in points]))
        print(points)
    try:
        mycursor.execute('INSERT INTO map(LivingRoom) VALUES (%s)', (points,))
        print ( mycursor)
        mydb.commit()
        mycursor.close()
        print('data successfully inserted ')
        return redirect ('/map')       
    except:
        print("An error has occured")        
    return redirect('/map')    

@auth.route ('/Bedroom',methods = ['POST','GET']) 
def Bedroom ():
    mycursor = mydb.cursor()
    print ( mycursor)
    if request.method == 'POST': 
        points = request.get_json()
        print (points)
        points =  ("".join([str(elem) for elem in points]))
        print(points)
    try:
        mycursor.execute('INSERT INTO map(Bedroom) VALUES (%s)', (points,))
        print ( mycursor)
        mydb.commit()
        mycursor.close()
        print('data successfully inserted ')
        return redirect ('/map')       
    except:
        print("An error has occured")        
    return redirect('/map')


@auth.route ('/sign_up', methods = ['POST','GET'])
def sign_up(): 
    if request.method == 'POST': 
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email = email).first()
        if user: 
            flash('Email already exist', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        #elif password1 != password2:
           # flash('Passwords don\'t match.', category='error')
        #elif len(password1) < 7:
           # flash('Password must be at least 7 characters.', category='error')
        
        else: 
            new_user = User (email = email, first_name= first_name, password = generate_password_hash(password1, method ='sha256'))
            db.session.add (new_user)
            db.session.commit ()
            login_user(new_user, remember=True)
            flash ('Account created', category='success')
            return redirect(url_for('views.home'))
            
       

    return render_template("sign_up.html", user=current_user)


@auth.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/questionnaire/')

def questionnaire(): 
    flash ('If you have not compile the questionnare, please start it!', category='success') 
    return render_template('questionnaire.html')




mycursor.execute ("SELECT * FROM report_question WHERE report_type_id IN (SELECT report_question_id FROM report_answer WHERE report_question_id = '1')")
print(mycursor)
question1 = mycursor.fetchall()
question1 = question1[0][3]
mycursor.execute ("SELECT * FROM report_question WHERE report_type_id IN (SELECT report_question_id FROM report_answer WHERE report_question_id = '2')")
print(mycursor)
question2 = mycursor.fetchall()
question2 = question2[0][3]
#
mycursor.execute ("SELECT * FROM report_question WHERE report_type_id IN (SELECT report_question_id FROM report_answer WHERE report_question_id = '4')")
print(mycursor)
question4 = mycursor.fetchall()
question4 = question4[0][3]
mycursor.execute ("SELECT * FROM report_question WHERE report_type_id IN (SELECT report_question_id FROM report_answer WHERE report_question_id = '3')")
print(mycursor)
question3 = mycursor.fetchall()
question3 = question3[0][3]
mycursor.execute ("SELECT * FROM report_question WHERE report_type_id IN (SELECT report_question_id FROM report_answer WHERE report_question_id = '5')")
print(mycursor)
question5 = mycursor.fetchall()
question5 = question5[0][3]
mycursor.execute ("SELECT * FROM report_question WHERE report_type_id IN (SELECT report_question_id FROM report_answer WHERE report_question_id = '6')")
print(mycursor)
question6 = mycursor.fetchall()
question6 = question6[0][3]
mycursor.execute ("SELECT * FROM report_question WHERE report_type_id IN (SELECT report_question_id FROM report_answer WHERE report_question_id = '7')")
print(mycursor)
question7 = mycursor.fetchall()
question7 = question7[0][3]
mycursor.execute ("SELECT * FROM report_question WHERE report_type_id IN (SELECT report_question_id FROM report_answer WHERE report_question_id = '8')")
print(mycursor)
question8 = mycursor.fetchall()
question8 = question8[0][3]


#estraggo risposte
mycursor.execute ("SELECT * FROM report_answer WHERE report_question_id IN (SELECT report_type_id FROM report_question WHERE report_type_id = '1')")
print(mycursor)
answer = mycursor.fetchall()
answer1= []
for i in range( len(answer)): 
    answer1.append(answer[i][3])
    
mycursor.execute ("SELECT * FROM report_answer WHERE report_question_id IN (SELECT report_type_id FROM report_question WHERE report_type_id = '2')")
print(mycursor)
answer = mycursor.fetchall()
answer2= []
for i in range( len(answer)): 
    answer2.append(answer[i][3])    

mycursor.execute ("SELECT * FROM report_answer WHERE report_question_id IN (SELECT report_type_id FROM report_question WHERE report_type_id = '4')")
print(mycursor)
answer = mycursor.fetchall()
answer4= []
for i in range( len(answer)): 
    answer4.append(answer[i][3])
mycursor.execute ("SELECT * FROM report_answer WHERE report_question_id IN (SELECT report_type_id FROM report_question WHERE report_type_id = '3')")
print(mycursor)
answer = mycursor.fetchall()
answer3= []
for i in range( len(answer)): 
    answer3.append(answer[i][3])

mycursor.execute ("SELECT * FROM report_answer WHERE report_question_id IN (SELECT report_type_id FROM report_question WHERE report_type_id = '5')")
print(mycursor)
answer = mycursor.fetchall()
answer5= []
for i in range( len(answer)): 
    answer5.append(answer[i][3])

mycursor.execute ("SELECT * FROM report_answer WHERE report_question_id IN (SELECT report_type_id FROM report_question WHERE report_type_id = '6')")
print(mycursor)
answer = mycursor.fetchall()
answer6= []
for i in range( len(answer)): 
    answer6.append(answer[i][3])

mycursor.execute ("SELECT * FROM report_answer WHERE report_question_id IN (SELECT report_type_id FROM report_question WHERE report_type_id = '7')")
print(mycursor)
answer = mycursor.fetchall()
answer7= []
for i in range( len(answer)): 
    answer7.append(answer[i][3])

mycursor.execute ("SELECT * FROM report_answer WHERE report_question_id IN (SELECT report_type_id FROM report_question WHERE report_type_id = '8')")
print(mycursor)
answer = mycursor.fetchall()
answer8= []
for i in range( len(answer)): 
    answer8.append(answer[i][3])

#associazione domande e risposte 
original_questions ={question1:[answer1[0],answer1[1],answer1[2],answer1[3]], 
        question2:[answer2[0],answer2[1],answer2[2],answer2[3]],
        question3:[answer3[0],answer3[1],answer3[2]], 
        question4:[answer4[0],answer4[1],answer4[2],answer4[3]],
        question5:[answer5[0],answer5[1],answer5[2]],
        question6:[answer6[0],answer6[1],answer6[2],answer6[3]],
        question7:[answer7[0],answer7[1],answer7[2]],
        question8:[answer8[0],answer8[1]]
        }


questions = copy.deepcopy(original_questions)


@auth.route('/start/')
def start():
    questions_shuffled = questions
    flash ('Please, answer to the questions!', category='success') 

    return render_template('start.html', q = questions_shuffled, o = questions)
    
@auth.route('/saveanswer', methods=['POST'])
def saveanswer():
    if request.method == 'POST': 
         for i in questions.keys():
                mycursor = mydb.cursor()
                print(mydb)
                answers= request.form.get("options{}".format(i)) #salvare i dati in db.
                print(answers)
                
                datetime_object = datetime.datetime.now()
                mycursor.execute ("INSERT INTO report_answer_question(description,date_reported) VALUES (%s,%s)",(answers, datetime_object))
                mydb.commit() 
                print(mycursor)
                
                mycursor.execute ("SELECT report_question_id,id FROM report_answer WHERE description IN (SELECT description FROM report_answer_question WHERE id=(SELECT MAX(id) FROM report_answer_question))")
                print(mycursor)
                schedule = mycursor.fetchall() 
                print(schedule)
                datetime_object = datetime.datetime.now()
                print(datetime_object)
                mycursor.execute ("INSERT INTO schedule (report_question_id, report_answer_id,description, date_created) VALUES (%s,%s,%s,%s)", (schedule[0][0], schedule[0][1], answers, datetime_object))
                mydb.commit()
                mycursor.close()
        

    return  redirect('/questionnaire')

@auth.route('/barchart',methods = ['POST','GET'])
def barchart():  
   
    yaw1 = []
    pose1 = [] 
    if request.method == 'POST': 
        pose = request.get_json()
        pose =  ("".join([str(elem) for elem in pose]))
        print(type(pose)) 
        pose1.append(pose)
        pose1 = ast.literal_eval(str(pose1))
        print(type(pose1))
        print (pose1)   
        print("---->>>>>>> Questa è la POSA : ", pose1)
        #yaw = request.get_json()
        #print (yaw)
        #yaw =  ("".join([str(elem) for elem in yaw]))
        #yaw1.append(yaw)    
       # print(type(yaw1)) 
       
        #print("---->>>>>>> Questa è lo yaw: ", yaw1)
        print("Sono qui")
        print( "--->Pose:",pose1[0][1]) 
        #mydb= getConnection()
        #mycursor= mydb.cursor() 
        #mycursor.execute("SELECT image FROM map WHERE image IS NOT NULL" )  
        #print(mycursor)
       # print ( " sono qui----")
        #image = mycursor.fetchall() 
        #image_map = image[-1]
        #print ( "tipo immagine", type(image))
       # image_map = base64.b64encode(image[0])
        #image_map = (image_map.decode( "UTF-8"))
       # print ( "immagine: ", image_map )
       # return render_template('barchart.html')

    mydb= getConnection()
    mycursor= mydb.cursor()
    mycursor.execute ("SELECT height FROM map WHERE height IS NOT NULL")
    height = mycursor.fetchall()
    height = height[-1:]
    print("------", height)
    #print(type(height))
    mycursor.execute ("SELECT width FROM map WHERE width IS NOT NULL")
    width = mycursor.fetchall()
    width = width[-1:]
    #print(type(width))
   # pose2= [ast.literal_eval(x) for x in pose1] 
    print("this is the pose1 ", pose1 )
    
    print (width[0][0])
    pose2 = pose1
    print("this is the pose2 ", pose2 )
    print("this is the pose2 ", type(pose2))
    #print(type(pose2[0]))

            #pose1 = int(pose1[0][0]['x'])
            #width = width[0][0]
            #pose1 = int(pose1[0][0]['x'])     
     
    if len(pose2)!= 0: 
     pose2= [ast.literal_eval(x) for x in pose2]     
     print( "??", type(pose2[0][0]['x']))
     screenx = int(width[0][0]) - int(pose2[0][0]['x'])
     screeny = int(width[0][0]) - int(pose2[0][0]['y'])
     print("ho scelto questo")
   
    else: 
        screenx = int(width[0][0]) - 0
        screeny = int(width[0][0]) - 0
       # my_dict = {"screen":[]}
            #my_dict["screen"].append(screenx)

            #print(type(pose1[0][0]['x']))
            #print ( type ( width[0][0]))
            #print("differenza" , screenx)
            #print("this is the x: ", screenx)
    #screeny = int(height[0][0]) - int(pose1[0][0]['y']) 
            #print("this is the y:", screeny) 
            #screenYaw = - math.pi / 2 - yaw1 
            #screenx = screenx + math.cos(screenYaw)
            #screeny = screeny + math.sin(screenYaw)
            
            #jpg_original = base64.b64decode(image_map)
            #jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
            #img = cv2.imdecode(jpg_as_np, flags=1)
        
            #image2 = cv2.circle (img, (screenx,screeny), radius=6, color=(0, 0, 255), thickness=-1)
    print('-----------------------------------------------------------------------------')  
            #image_map2 = base64.b64encode(image2)
            #image_map2 = (image_map2.decode( "UTF-8"))
            #mycursor.execute('INSERT INTO map(image) VALUES (%)', image_map )
        # mydb.commit()
            
            #print ( "this is the image 2", image_map2)

    print ( "sto inviando il file ----" , screenx)
    #mycursor.execute("SELECT * FROM pir ORDER BY realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE")
    mycursor.execute("SELECT * FROM pir ORDER BY realtime DESC limit 20") 
    last_activation = mycursor.fetchall()
    print("ultima attivazione", last_activation)
    distance = []
    number_pir = []
    for i in range(len(last_activation)):
      distance.append(last_activation[i][3]/math.sqrt(3))
      number_pir.append( last_activation[i][0])
    print("questo è il number_pir", number_pir )
    print("questo è il number_pir", type(number_pir))  
  
    direzionex.append(screenx)
    print ("------", direzionex)
    direzioney.append(screeny)
    print ("------", direzioney)
    person_posx = []
    person_posy = []
    for i in range(len(number_pir)): 
        if len(direzionex)>1 and  (direzionex[-1] > direzionex[-2] and direzioney[-1] > direzioney[-2]):
            if number_pir[i] == 4: 
        
                person_posx.append(screenx + distance[i] )
                person_posy.append(screeny + distance[i])   
                print("condizione 1")
            if number_pir[i] == 3: 
                person_posx.append(screenx - distance[i]) 
                person_posy.append(screeny + distance[i]) 
            if number_pir[i] == 6: 
                person_posx.append(screenx - distance [i])
                person_posy.append(screeny - distance[i])
            if number_pir[i] == 5: 
                person_posx.append(screenx + distance [i]) 
                person_posy.append(screeny - distance[i]) 

        if len(direzionex)>1 and (direzionex[-1] < direzionex[-2] and direzioney[-1] < direzioney[-2]):      
            if number_pir[i] == 4 : 
                person_posx.append(screenx -distance[i])
                person_posy.append(screeny  - distance[i]) 
                print("condizione 2")
            if number_pir[i] == 3: 
                person_posx.append(screenx + distance[i]) 
                person_posy.append(screeny - distance[i]) 
            if number_pir[i] == 6: 
                person_posx.append(screenx + distance[i])
                person_posy.append(screeny + distance[i])
            if number_pir[i] == 5: 
                person_posx.append(screenx - distance[i]) 
                person_posy.append(screeny + distance[i]) 


        if len(direzionex)>1 and (direzionex[-1] > direzionex[-2] and direzioney[-1] < direzioney[-2]):
            if number_pir [i] == 4: 
                person_posx.append(screenx + distance[i])
                person_posy.append(screeny  - distance [i])  
                print("condizione 3")
            if number_pir [i] == 3: 
                person_posx.append( screenx + distance[i] )
                person_posy.append(screeny + distance[i])
            if number_pir [i] == 6: 
                person_posx.append(screenx - distance[i])
                person_posy.append (screeny + distance[i])
            if number_pir [i]== 5: 
                person_posx.append (screenx - distance[i]) 
                person_posy.append( screeny - distance [i])
        if len(direzionex)>1 and (direzionex[-1] < direzionex[-2] and direzioney[-1] > direzioney[-2]):
            if number_pir [i] == 4: 
                person_posx .append ( screenx - distance [i])
                person_posy .append (screeny  + distance [i])    
                print("condizione 4")
                print("person_posx",  person_posx)
            if number_pir [i] == 3: 
                person_posx .append(screenx - distance[i]) 
                person_posy.append( screeny - distance [i]) 
            if number_pir [i] == 6: 
                person_posx .append( screenx + distance [i])
                person_posy.append( screeny - distance [i])
            if number_pir [i] == 5: 
                person_posx.append(screenx + distance [i]) 
                person_posy.append(screeny + distance [i])
        else : 
            if number_pir [i] == 4: 
                person_posx.append(screenx + distance [i])
                person_posy.append(screeny + distance [i])
                print("condizione 1")
            if number_pir [i] == 3: 
                person_posx.append(screenx - distance [i])
                person_posy.append(screeny + distance [i] )
            if number_pir [i] == 6: 
                person_posx.append( screenx - distance [i])
                person_posy.append(screeny - distance [i])
            if number_pir [i] == 5: 
                person_posx.append(screenx + distance [i])
                person_posy.append( screeny - distance [i]) 

    #RICOSTRUZIONE DELLA DASHBOARD   
   # mycursor = mydb.cursor()
    mycursor.execute ("SELECT report_question_id FROM schedule")
    print(mycursor)
    report_question_id= mycursor.fetchall()
    report_question_id= report_question_id[-8:]    
    print(report_question_id[-8:])

    mycursor.execute ("SELECT description FROM schedule")
    print(mycursor)
    description= mycursor.fetchall()  
    description= description[-8:]
    print(description[-8:])

    mycursor.execute ("SELECT date_created FROM schedule")
    print(mycursor)
    date_created= mycursor.fetchall()
    date_created= date_created[-1:]  
    date_created = date_created[0][0][0:10]
    print(date_created[-1:])

        #RICOSTRUZIONE DELLE COORDINATE PER LA MAPPA 
    mycursor.execute ("SELECT Kitchen FROM map WHERE Kitchen IS NOT NULL")
    Kitchen_coor= mycursor.fetchall()
    Kitchen_coor= Kitchen_coor[-1:][0]  
    print(Kitchen_coor)

    import datetime
    from datetime import timedelta

    labels = []
    values =[]
    for i in range(len(report_question_id)): 
            if report_question_id[i][0]==1 and  description[i][0] == '6:00-7:00 a.m.': 
                values.append('100')
                labels.append('6:00-7:00')
            if report_question_id[i][0]==1 and  description[i][0] == '7:00-8:00 a.m.': 
                values.append('100')
                labels.append('7:00-8:00')
            if report_question_id[i][0]==1 and  description[i][0] == '8:00-9:00 a.m.': 
                values.append('100')
                labels.append('8:00-9:00')
            if report_question_id[i][0]==1 and  description[0][0] == 'after 9:00 a.m.': 
                values.append('100')
                labels.append('9:00-10:00')
            if report_question_id[i][0]==4 and  description[i][0] == '0-30 minutes after waked up': 
                values.append('100')
                time = labels[0].split('-')
            
                date_time_obj = datetime.datetime.strptime(time[1], '%H:%M')
                final = date_time_obj+timedelta(minutes = 30)
                final_time_str = final.strftime('%H:%M')
                final_time_str = time[1]+'-'+final_time_str+'a.m.'
                labels.append(final_time_str)
            if report_question_id[i][0]==4 and  description[i][0] == '30 minutes-1 hour after waked up': 
                values.append('100')
                time = labels[0].split('-')
            
                date_time_obj = datetime.datetime.strptime(time[1], '%H:%M')
                initial = date_time_obj+timedelta(minutes = 30)
                initial_time_str = initial.strftime('%H:%M')    
                date_time_obj = datetime.datetime.strptime(time[1], '%H:%M')
                final = date_time_obj+timedelta(minutes = 30, hours = 1)
                final_time_str = final.strftime('%H:%M')
                final_time_str =  initial_time_str +'-'+final_time_str 
                labels.append(final_time_str)        
            if report_question_id[i][0]==4 and  description[i][0] == 'I do not have breakfast':
                labels.append('')  
                values.append('0')
            if report_question_id[i][0]==4 and  description[i][0] == 'other': 
                labels.append('') 
                values.append('0')

            if report_question_id[i][0]==6 and  description[i][0] == '18:00-19:00 p.m.': 
                values.append('100')
                labels.append('18:00-19:00')
            if report_question_id[i][0]==6 and  description[i][0] == '19:00-20:00 p.m.': 
                values.append('100')
                labels.append('19:00-20:00')
            if report_question_id[i][0]==6 and  description[i][0] == 'after 20:00 p.m.': 
                values.append('100')
                labels.append('20:00-21:00')
            if report_question_id[i][0]==6  and  description[i][0] == 'before 18:00 p.m.': 
                values.append('100')
                labels.append('17:30-18:00')

            if report_question_id[i][0]==2 and  description[i][0] == '11:00-12:00 a.m.': 
                values.append('100')
                labels.append('11:00-12:00')
            if report_question_id[i][0]==2 and  description[i][0] == '12:00-13:00 p.m.': 
                values.append('100')
                labels.append('12:00-13:00')
            if report_question_id[i][0]==2 and  description[i][0] == '13:00-14:00 p.m.': 
                values.append('100')
                labels.append('13:00-14:00')
            if report_question_id[i][0]==2  and  description[i][0] == 'after 14:00 p.m.': 
                values.append('100')
                labels.append('after 14:00')
            
    print(labels) 
    labels1 = []
    labels11 = [labels[0],labels[2],labels[1],labels[3]]
    print(labels11)
    labels1 = [labels[0]+ ' wake up',labels[2] +' breakfast',labels[1] +' lunch',labels[3]+' dinner']
    print("---------- labels", json.dumps(labels1))
    print(values)
    date_time = []
    for i in range(len(labels)):
                time = labels[i].split('-')
            
                date_time.append(time[0])
                date_time.append(time[1])

    print(date_time)
    mycursor.execute("SELECT image FROM map WHERE image IS NOT NULL" )  
    print(mycursor)
    image = mycursor.fetchall() 
    image = image[-1]
    image_map = image[0].decode("UTF-8")
    #print th e position of the robot based ion pose
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    print(current_time)
    for date_times in date_time: 
            if date_times in current_time:
                date_times = date_time.index(date_times)
                print (date_times)
                if date_times == 1 or date_times == 0 : 
                    mycursor.execute("SELECT bedroom FROM map WHERE bedroom IS NOT NULL")
                    bedroom = mycursor.fetchall()
                    bedroom = bedroom[-1:]
                    bedroom = bedroom[0]
                    bedroom = bedroom[0]
                    bedroom = bedroom.replace('[', '')
                    bedroom = bedroom.replace(']','')
                    bedroom = bedroom.split(',')
                    bedroom = np.asarray([int(x) for x in bedroom])
                    bedroom = bedroom.reshape (int(len(bedroom)/2),-1)
                    x  =  [p[0] for p in bedroom]
                    y = [p[1] for p in bedroom]
                    centroid =( sum(x)/ len(bedroom),sum(y)/len(bedroom))
                    mycursor.execute ("SELECT height FROM map WHERE height IS NOT NULL")
                    height = mycursor.fetchall()
                    height = height[-1:]
                    mycursor.execute ("SELECT width FROM map WHERE width IS NOT NULL")
                    width = mycursor.fetchall()
                    width = width[-1:]
                

    #PUO ESSERE DEFINITA COME UNA FUNZIONE 
                    x = height/768
                    y = width / 1024
                    x_r = centroid[0]/x
                    y_r = centroid[1]/y
                    x_rr = height - x_r
                    y_rr = width - y_r
                    filename = {
                        "Skill" : "c31fabff-0663-4577-b6ec-ce5ae764b5e1",
                        "EventName": "localization1",
                        "Payload": {
                        "CustomKey": x_rr ,
                        "AnotherKey": y_rr
                            },
                        "Source": "EventSender"
                            }
                    headers = {
                    "Content-Type": "application/json"
                            }
                    activate_robot = requests.post('http://192.168.0.106/api/skills/event/',json.dumps(filename),headers=headers)
                global place  #settata come variabile globale potrebbe dare errori 
                if date_times == 2 or date_times == 3 :
                    place = description[4]
                elif date_times == 4 or date_times == 5 : 
                    place = description[2]
                elif  date_times == 5 or date_times == 6: 
                    place = description[6]
                
               # mycursor= mydb.cursor()
                mycursor.execute ("SELECT " + place[0] + " FROM map WHERE "+place[0]+ " IS NOT NULL")
                room = mycursor.fetchall()
                #mycursor.close()
                room = room[-1:]
                room = room[-1:]
                room = room[0]
                room = room.replace('[', '')
                room = room.replace(']','')
                room = room.split(',')
                room = np.asarray([int(x) for x in bedroom])
                room = bedroom.reshape (int(len(bedroom)/2),-1)
                x  =  [p[0] for p in bedroom]
                y = [p[1] for p in bedroom]
                centroid =( sum(x)/ len(bedroom),sum(y)/len(bedroom))
                mycursor.execute ("SELECT height FROM map WHERE height IS NOT NULL")
                height = mycursor.fetchall()
                height = height[-1:]
                mycursor.execute ("SELECT width FROM map WHERE width IS  IS NOT NULL")
                width = mycursor.fetchall()
                width = width[-1:]
    #PUO ESSERE DEFINITA COME UNA FUNZIONE 
                x = height/768
                y = width / 1024
                x_r = centroid[0]/x
                y_r = centroid[1]/y
                x_rr = height - x_r
                y_rr = width - y_r
                path = x_rr + ':'+ y_rr
                filename = {
                        "Skill" : "c31fabff-0663-4577-b6ec-ce5ae764b5e1",
                        "EventName": "localization1",
                        "Payload": {
                        "CustomKey": path 
                    
                            },
                        "Source": "EventSender"
                            }
                headers = {
                    "Content-Type": "application/json"
                            }
            
                activate_robot = requests.post('http://192.168.0.106/api/skills/event/',json.dumps(filename),headers=headers)
        #recupera i dati delle attivazioni dei pir dal database è ti dice dove lo ha trovato. 

                mycursor.execute("SELECT * FROM pir WHERE realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE)") 
                activation = mycursor.fetchall()
                mycursor.execute("SELECT * FROM pir2 WHERE realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE)") 
                activation2 = mycursor.fetchall()  
                mycursor.execute("SELECT * FROM pir3 WHERE realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE)") 
                activation3 = mycursor.fetchall()  
                mycursor.execute("SELECT * FROM pir4 WHERE realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE)") 
                activation4 = mycursor.fetchall() 
                activation_final = activation+activation2+activation3+activation4
                activation_final.sort(key=lambda y: y[2])
                df = pd.DataFrame( activation_final, columns=['analvalue', 'time', 'realtime','distance'])
                start = 0
                activation= []
                time = df['realtime'].dt.second
                time = time.value_counts()
                time = time.sort_index()
                for i in range(len(time)): 
                    stop = start + time[time.index[i]]
                    activation.append (np.bincount(activation_final[start:stop]).argmax())       
                    # time_index.append(np.bincount(time[start:stop]).argmax())
                    start = stop
                    color = (0, 255, 0)     
                    start = 0
                    count = 0 



                for j in range(len(activation)): 
                    stop = start+3
                    valuest = activation[start:stop]
                    valuest = np.array(valuest)
                    valuest = valuest.reshape (-3,3)
                if model.predict (valuest) ==  '':
                    
                    if  (valuest [0][0]==2  &  valuest[0][1] == 4): 
                    
                        cv2.arrowedLine(image_map,[200,300], [100,200],color )
                        cv2.arrowedLine(image_map, [100,200], [200,300],color )
                    # cv2.imshow('img', img)
                    # cv2.waitKey(0)
                        
                        start = stop 
                    elif (valuest [0][0] ==2  &   valuest[0][1]  == 3): 
                        cv2.arrowedLine(image_map,[200,300], [300,200],color)
                        cv2.arrowedLine(image_map,[300,200],[200,300] ,color)
                        # cv2.imshow('img', img)
                        #cv2.waitKey(0)
                        start = stop 
                    
                    elif (valuest [0][0] ==3  &   valuest[0][1] == 1): 
                        cv2.arrowedLine(image_map,[300,200], [200,100],color)
                        cv2.arrowedLine(image_map,[200,100],[300,200], color)
                        #cv2.imshow('img', img)
                        #cv2.waitKey(0)
                        start = stop 
                    elif (valuest [0][0] ==3  &   valuest[0][1]== 2): 
                        cv2.arrowedLine(image_map,[300,200], [200,300],color)
                        cv2.arrowedLine(image_map, [200,300],[300,200],color)
                        #cv2.imshow('img', img)
                        #cv2.waitKey(0)
                        start = stop 
                    
                    elif (valuest [0][0] ==1  &  valuest[0][1] == 3): 
                        cv2.arrowedLine(image_map,[200,100], [300,200],color)
                        cv2.arrowedLine(image_map, [300,200],[200,100],color)
                        # cv2.imshow('img', img)
                        #cv2.waitKey(0)
                        start = stop 
                    elif (valuest [0][0] ==1  &  valuest[0][1]== 4): 
                        cv2.arrowedLine(image_map,[200,100], [100,200],color)
                        cv2.arrowedLine(image_map,[100,200],[200,100], color)
                        #cv2.imshow('img', img)
                        #cv2.waitKey(0)
                        start = stop 
                    elif (valuest [0][0] ==4 &   valuest[0][1] == 1): 
                        cv2.arrowedLine(image_map,[100,200], [200,100],color)
                        cv2.arrowedLine(image_map,[200,100],[100,200], color)
                        # cv2.imshow('img', img)
                        #cv2.waitKey(0)
                        start = stop 
                    
                    elif (valuest [0][0]==4  &   valuest[0][1] == 2): 
                        cv2.arrowedLine(image_map,[100,200], [200,300],color)
                        cv2.arrowedLine(image_map,[200,300],[100,200], color)
                        #  cv2.imshow('img', img)
                        # cv2.waitKey(0)
                        start = stop 
                    
                    if model.predict (valuest)  == 'move and still':
                        if  (valuest [0][0] ==2  &   valuest[0][1]== 4): 
                    
                          cv2.arrowedLine(image_map,[200,300], [100,200],color )
                        # cv2.imshow('img', img)
                        #cv2.waitKey(0)
                          start = stop 
                        elif(valuest [0][0]==2  &   valuest[0][1]== 3): 
                            cv2.arrowedLine(image_map,[200,300], [300,200],color)
                            
                            # cv2.imshow('img', img)
                            #cv2.waitKey(0)
                            start = stop 
                        
                        elif (valuest [0][0] ==3  &   valuest[0][1] == 1): 
                            cv2.arrowedLine(image_map,[300,200], [200,100],color)
                            #cv2.imshow('img', img)
                            #cv2.waitKey(0)
                            start = stop 
                        elif (valuest [0][0] ==3  &   valuest[0][1]== 2): 
                            cv2.arrowedLine(image_map,[300,200], [200,300],color)
                            #cv2.imshow('img', img)
                            #cv2.waitKey(0)
                            start = stop 
                        
                        elif (valuest [0][0] ==1  &   valuest[0][1] == 3): 
                            cv2.arrowedLine(image_map,[200,100], [300,200],color)
                            # cv2.imshow('img', img)
                            # cv2.waitKey(0)
                            start = stop 
                        elif (valuest [0][0]==1  &   valuest[0][1] == 4): 
                            cv2.arrowedLine(image_map,[200,100], [100,200],color)
                            #cv2.imshow('img', img)
                            #cv2.waitKey(0)
                            start = stop 
                        elif (valuest [0][0]==4 &   valuest[0][1]== 1): 
                            cv2.arrowedLine(image_map,[100,200], [200,100],color)
                            # cv2.imshow('img', img)
                            #cv2.waitKey(0)
                            start = stop 
                        
                        elif (valuest [0][0]==4  &  valuest[0][1]== 2): 
                            cv2.arrowedLine(image_map,[100,200], [200,300],color)
                            #cv2.imshow('img', img)
                            #cv2.waitKey(0)
                            start = stop 
                        
                    elif  model.predict (valuest)  == 'not allowed':
                        count = count+1 
                        start = stop

                    cv2.imshow('img', image_map)
                    cv2.waitKey(0)

    print("---->",person_posx)
    print("---->",person_posy)
    return  render_template('barchart.html', labels = json.dumps(labels1), values = json.dumps(values),date_created = json.dumps(date_created), image = image_map, datax = screenx, datay = screeny, personx=person_posx, persony=person_posy )
        


@auth.route('/recivemessage', methods = ['POST','GET','PUT'])
def receivemessage(): 
    print(" sono qui")
    if request.method == 'POST':
        recivemessage = request.args.get("data")
        print(recivemessage) 
        print ( type(recivemessage))
        print("il metodo è post")
        recivemessage1 = recivemessage.split(',')
        print(recivemessage1)
        mycursor.execute('INSERT INTO pir(analvalue,time,realtime,distance) VALUES (%s,%s,%s,%s)', (recivemessage1[0],recivemessage1[1],recivemessage1[2],recivemessage1[3]))
        mydb.commit()
       # mycursor.close()
         
         # mycursor.execute('INSERT INTO pir2(analvalue2,time2,realtime2,distance) VALUES (%s,%s,%s,%s)', (recivemessage[1],recivemessage[2],recivemessage[3],recivemessage[4]))
          #mydb.commit()
          #mycursor.close()
        #elif recivemessage[0] == '5': 
         # mycursor.execute('INSERT INTO pir3(analvalue3,time3,realtime3,distance) VALUES (%s,%s,%s,%s)', (recivemessage[1],recivemessage[2],recivemessage[3],recivemessage[4]))
          #mydb.commit()
          #mycursor.close()
        #elif recivemessage[0] == '6': 
         # mycursor.execute('INSERT INTO pir4(analvalue4,time4,realtime4,distance) VALUES (%s,%s,%s,%s)', (recivemessage[1],recivemessage[2],recivemessage[3],recivemessage[4]))
          #mydb.commit()
          #mycursor.close()
        
           
    return '''
              <h1>The language value is: {}</h1>
              '''.format(recivemessage)

@auth.route("/predict", methods = ["POST"])
def predict(): 
    mycursor.execute("SELECT * FROM pir WHERE realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE)") 
    activation = mycursor.fetchall()
    mycursor.execute("SELECT * FROM pir2 WHERE realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE)") 
    activation2 = mycursor.fetchall()  
    mycursor.execute("SELECT * FROM pir3 WHERE realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE)") 
    activation3 = mycursor.fetchall()  
    mycursor.execute("SELECT * FROM pir4 WHERE realtime >= DATE_SUB(NOW(),INTERVAL 1 MINUTE)") 
    activation4 = mycursor.fetchall() 
    activation_final = activation+activation2+activation3+activation4
    activation_final.sort(key=lambda y: y[2])
    df = pd.DataFrame( activation_final, columns=['analvalue', 'time', 'realtime','distance'])
    start = 0
    activation= []
    time = df['realtime'].dt.second
    time = time.value_counts()
    time = time.sort_index()
    for i in range(len(time)): 
      stop = start + time[time.index[i]]
      activation.append (np.bincount(activation_final[start:stop]).argmax())       
    # time_index.append(np.bincount(time[start:stop]).argmax())
      start = stop
    color = (0, 255, 0)     
    start = 0
    count = 0 



    for j in range(len(activation)): 
     stop = start+3
     valuest = activation[start:stop]
     valuest = np.array(valuest)
     valuest = valuest.reshape (-3,3)
    if model.predict (valuest) ==  'back and forth ':
        
       if  (valuest [0][0]==2  &  valuest[0][1] == 4): 
       
        cv2.arrowedLine(img,[200,300], [100,200],color )
        cv2.arrowedLine(img, [100,200], [200,300],color )
       # cv2.imshow('img', img)
       # cv2.waitKey(0)
           
        start = stop 
       elif (valuest [0][0] ==2  &   valuest[0][1]  == 3): 
           cv2.arrowedLine(img,[200,300], [300,200],color)
           cv2.arrowedLine(img,[300,200],[200,300] ,color)
          # cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
      
       elif (valuest [0][0] ==3  &   valuest[0][1] == 1): 
           cv2.arrowedLine(img,[300,200], [200,100],color)
           cv2.arrowedLine(img,[200,100],[300,200], color)
           #cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
       elif (valuest [0][0] ==3  &   valuest[0][1]== 2): 
           cv2.arrowedLine(img,[300,200], [200,300],color)
           cv2.arrowedLine(img, [200,300],[300,200],color)
           #cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
    
       elif (valuest [0][0] ==1  &  valuest[0][1] == 3): 
           cv2.arrowedLine(img,[200,100], [300,200],color)
           cv2.arrowedLine(img, [300,200],[200,100],color)
          # cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
       elif (valuest [0][0] ==1  &  valuest[0][1]== 4): 
           cv2.arrowedLine(img,[200,100], [100,200],color)
           cv2.arrowedLine(img,[100,200],[200,100], color)
           #cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
       elif (valuest [0][0] ==4 &   valuest[0][1] == 1): 
           cv2.arrowedLine(img,[100,200], [200,100],color)
           cv2.arrowedLine(img,[200,100],[100,200], color)
          # cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
    
       elif (valuest [0][0]==4  &   valuest[0][1] == 2): 
           cv2.arrowedLine(img,[100,200], [200,300],color)
           cv2.arrowedLine(img,[200,300],[100,200], color)
         #  cv2.imshow('img', img)
          # cv2.waitKey(0)
           start = stop 
    
    if model.predict (valuest)  == 'move and still':
        if  (valuest [0][0] ==2  &   valuest[0][1]== 4): 
       
           cv2.arrowedLine(img,[200,300], [100,200],color )
          # cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
        elif (valuest [0][0]==2  &   valuest[0][1]== 3): 
           cv2.arrowedLine(img,[200,300], [300,200],color)
          
          # cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
      
        elif (valuest [0][0] ==3  &   valuest[0][1] == 1): 
           cv2.arrowedLine(img,[300,200], [200,100],color)
           #cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
        elif (valuest [0][0] ==3  &   valuest[0][1]== 2): 
           cv2.arrowedLine(img,[300,200], [200,300],color)
           #cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
    
        elif (valuest [0][0] ==1  &   valuest[0][1] == 3): 
           cv2.arrowedLine(img,[200,100], [300,200],color)
          # cv2.imshow('img', img)
          # cv2.waitKey(0)
           start = stop 
        elif (valuest [0][0]==1  &   valuest[0][1] == 4): 
           cv2.arrowedLine(img,[200,100], [100,200],color)
           #cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
        elif (valuest [0][0]==4 &   valuest[0][1]== 1): 
           cv2.arrowedLine(img,[100,200], [200,100],color)
          # cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
    
        elif (valuest [0][0]==4  &  valuest[0][1]== 2): 
           cv2.arrowedLine(img,[100,200], [200,300],color)
           #cv2.imshow('img', img)
           #cv2.waitKey(0)
           start = stop 
    
    elif  model.predict (valuest)  == 'not allowed':
        count = count+1 
        start = stop

    cv2.imshow('img', img)
    cv2.waitKey(0)

    return render_template ("barchart.html")