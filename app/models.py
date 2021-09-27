# Table models to initialize database

from app import db
from datetime import datetime
from app import login
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(Uid):
    return User.query.get(int(Uid))

# Model for Table user
# Function: log all info for registered users
class User(UserMixin,db.Model):
    Uid = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    likes = db.Column(db.Integer)
    phone = db.Column(db.String(11))
    address = db.Column(db.String(128))
    description = db.Column(db.String(1024))
    recipe = db.relationship('Recipes', backref='contributor', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def get_id(self):
        return (self.Uid)

    def set_password(self,password):
        self.password=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)

# Model for Table recipes
# Function: log all base info for recipes
class Recipes(db.Model):
    Rid = db.Column(db.Integer, primary_key=True)
    Uid = db.Column(db.Integer, db.ForeignKey('user.Uid'))
    sumlikes = db.Column(db.Integer)
    dailylikes = db.Column(db.Integer)
    name = db.Column(db.String(64))
    ingredient_id = db.Column(db.Integer)   #not use
    method = db.Column(db.String(1024))
    type = db.Column(db.String(1024))
    step_id = db.Column(db.Integer)         #not use
    ####date "YYYYMMDD" time "HHMMSS"
    date = db.Column(db.Integer)
    time = db.Column(db.Integer)
    description = db.Column(db.String(1024))
    update_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Recipes {}>'.format(self.name)

    def get_id(self):
        return (self.Rid)

# Model for Table subscribe
# Function: log when a user followed other people
class Subscribe(db.Model):
    Sid = db.Column(db.Integer, primary_key=True)
    contributor = db.Column(db.Integer, db.ForeignKey('user.Uid'),index=True)
    explorer = db.Column(db.Integer, db.ForeignKey('user.Uid'),index=True)

    def __repr__(self):
        return '<Recipes {}>'.format(self.Sid)

    def get_id(self):
        return (self.Sid)

# Model for Table Like
# Function: log when a user liked a recipe
class Like(db.Model):
    Lid = db.Column(db.Integer, primary_key=True)
    explorer = db.Column(db.Integer, db.ForeignKey('user.Uid'), index=True)
    recipe = db.Column(db.Integer, db.ForeignKey('recipes.Rid'), index=True)
    date = db.Column(db.Integer)
    def __repr__(self):
        return '<Recipes {}>'.format(self.Lid)

    def get_id(self):
        return (self.Lid)


# Model for Table Ingredient
# Function: ingredients detail for Table recipe
class Ingredient(db.Model):
    IiD = db.Column(db.Integer, primary_key=True)
    recipe=db.Column(db.Integer, db.ForeignKey('recipes.Rid'), index=True)
    sequence=db.Column(db.Integer, index=True)
    type=db.Column(db.String(64), index=True)
    weight=db.Column(db.String(64))
    def __repr__(self):
        return '<Ingredient {}>'.format(self.type)

    def get_id(self):
        return (self.Iid)


# Model for Table StepDetail
# Function: step detail for Table recipe
class StepDetail(db.Model):
    Sid = db.Column(db.Integer, primary_key=True)
    recipe = db.Column(db.Integer, db.ForeignKey('recipes.Rid'), index=True)
    sequence = db.Column(db.Integer, index=True)
    description = db.Column(db.String(1024))

    def __repr__(self):
        return '<Ingredient {} Seq {}>'.format(self.recipe,self.sequence)

    def get_id(self):
        return (self.Sid)


# Model for Table comment
# Function: comment detail for Table recipe
class Comment(db.Model):
    Cid = db.Column(db.Integer, primary_key=True)
    recipe = db.Column(db.Integer, db.ForeignKey('recipes.Rid'), index=True)
    explorer = db.Column(db.Integer, db.ForeignKey('user.Uid'), index=True)
    content = db.Column(db.String(1024))
    date = db.Column(db.DateTime, index=True, default=datetime.now)


# Model for Table typelog
# Function: log users search custom
class typelog(db.Model):
    Name = db.Column(db.String(1024), primary_key=True)
    Number = db.Column(db.Integer)


# Model for Table methodlog
# Function: log users search custom
class methodlog(db.Model):
    Name = db.Column(db.String(1024), primary_key=True)
    Number = db.Column(db.Integer)




