import requests
import json
import mysql
import mysql.connector




from flask import Flask,jsonify,request
from flask_marshmallow import Marshmallow
import mysql.connector
from mysql.connector import Error
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow import ValidationError
#Sets up database
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://root:#Comco92505@localhost/fitness_center_db'
db=SQLAlchemy(app)
ma=Marshmallow(app)

class MemberSchema(ma.Schema):
    id = db.Column(db.Integer,primary_key=True)
    name = fields.String(required = True)
    email = fields.String(required = True)
    phone = fields.String(required = True)
    
    class Meta:
        fields=("name","email","phone","id")
        
member_schema=MemberSchema()
members_schema=MemberSchema(many=True)

class WorkoutSchema(ma.Schema):
    id = db.Column(db.Integer,primary_key=True)
    session= fields.String(required = True)
    day = fields.String(required = True)
    time = fields.String(required = True)
    member_id =fields.Integer(foreign_key=True)
    
    class Meta:
        fields=("workout_type","day","time","member_id","id")
        
workout_schema=WorkoutSchema()
workouts_schema=WorkoutSchema(many=True)

@app.route('/')
def home():
    return "Member and Workout Sessions"
#Sets up Tables
class Member(db.Model):
    __tablename__="member"
    id = db.Column(db.Integer,primary_key= True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
        
class Workout(db.Model):
    __tablename__="workout"
    id = db.Column(db.Integer,primary_key=True)
    workout_type =db.Column(db.String(255),nullable=False)
    day =db.Column(db.String(255),nullable=False)
    time =db.Column(db.String(255),nullable=False)
    member_id = db.Column(db.String(255),nullable=False)
 #Gets all member information   
@app.route('/member',methods=["GET"])
def get_member():
    member=Member.query.all()
    return members_schema.jsonify(member)
#Gets all workout session information
@app.route('/workout',methods=["GET"])
def get_workout():
    workout=Workout.query.all()
    return workouts_schema.jsonify(workout)
#Gets workout session by a specific member
@app.route('/workout/by-member_id',methods=["GET"])
def query_workout_by_member_id():
    member_id=request.args.get('member_id')
    workouts=Workout.query.filter_by(member_id=member_id).all()
    if workouts:
        return workouts_schema.jsonify(workouts)
    else:
        return jsonify({'message':"member not found"}),404
    
#Adds member
@app.route('/member',methods=['POST'])
def add_member():
    try:
        member_data=member_schema.load(request.json)
    except ValidationError as  err:
        return jsonify(err.messages),400
    new_member= Member(name=member_data['name'],email=member_data['email'],phone=member_data['phone'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message':'New Member added successfully'}),201
#Adds workout
@app.route('/workout',methods=['POST'])
def add_workout():
    try:
        workout_data=workout_schema.load(request.json)
    except ValidationError as  err:
        return jsonify(err.messages),400
    new_workout= Workout(workout_type=workout_data['workout_type'],day=workout_data['day'],time=workout_data['time'],member_id=workout_data['member_id'])                   
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({'message':'New Workout added successfully'}),201
#Updates member
@app.route('/member/<int:id>', methods=['PUT'])
def update_member(id):
    member =Member.query.get_or_404(id)
    try:
        member_data=member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    member.name=member_data['name']
    member.email=member_data['email']
    member.phone=member_data['phone']
    db.session.commit()
    return jsonify({"message":"Member data is updated successfully"}),200
#Updates workout session
@app.route('/workout/<int:id>', methods=['PUT'])
def update_workout(id):
    workout =Workout.query.get_or_404(id)
    try:
        workout_data=workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    workout.workout_type=workout_data['workout_type']
    workout.day=workout_data['day']
    workout.time=workout_data['time']
    workout.member_id=workout_data['member_id']
    db.session.commit()
    return jsonify({"message":"Workout Session is updated successfully"}),200
#Deletes member
@app.route('/member/<int:id>', methods=["DELETE"])
def delete_member(id):
    member=Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message":"Member removed successfully"}),200
  #Deletes workout  
@app.route('/workout/<int:id>', methods=["DELETE"])
def delete_workout(id):
    workout=Workout.query.get_or_404(id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message":"Workout session removed successfully"}),200
    
    
with app.app_context():
    db.create_all()
    
if __name__=='__main__':
    app.run(debug=True)
