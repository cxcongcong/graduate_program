from app import db
from app.models import User, Recipes, Like, Subscribe
import random
from datetime import datetime
from sqlalchemy import func
import numpy as np
# delete data


# 添加MR.A
def adduser():
    users = User.query.all()
    for user in users:
        db.session.delete(user)
    db.session.commit()
    u = User(id='MR.A',name='MR.A', email='A@unsw.com',  phone='11111111')
    u.set_password('aaa')
    db.session.add(u)
    db.session.commit()
    # 添加MR.B
    u = User(id='MR.B',name='MR.B', email='B@unsw.com',  phone='22222222')
    u.set_password('bbb')
    db.session.add(u)
    db.session.commit()
    # 添加MR.C
    u = User(id='MR.C',name='MR.C', email='C@unsw.com',  phone='33333333')
    u.set_password('ccc')
    db.session.add(u)
    db.session.commit()
    # 添加MR.D
    u = User(id='MR.D',name='MR.D', email='D@unsw.com',  phone='44444444')
    u.set_password('ddd')
    db.session.add(u)
    db.session.commit()
    # 添加MR.E
    u = User(id='MR.E',name='MR.E', email='E@unsw.com',  phone='55555555')
    u.set_password('eee')
    db.session.add(u)
    db.session.commit()
    # 添加MR.F
    u = User(id='MR.F',name='MR.F', email='F@unsw.com',  phone='66666666')
    u.set_password('fff')
    db.session.add(u)
    db.session.commit()
    # 添加MR.G
    u = User(id='MR.G',name='MR.G', email='G@unsw.com',  phone='77777777')
    u.set_password('ggg')
    db.session.add(u)
    db.session.commit()
    # 添加MR.H
    u = User(id='MR.H',name='MR.H', email='H@unsw.com', phone='88888888')
    u.set_password('hhh')
    db.session.add(u)
    db.session.commit()
    # 添加MR.I
    u = User(id='MR.I',name='MR.I', email='I@unsw.com',phone='99999999')
    u.set_password('iii')
    db.session.add(u)
    db.session.commit()
    # 添加MR.J
    u = User(id='MR.J',name='MR.J', email='J@unsw.com',phone='00000000')
    u.set_password('jjj')
    db.session.add(u)
    db.session.commit()


## ADD relation

def add_relation():
    like = Like.query.all()
    sub = Subscribe.query.all()

    for i in like:
        db.session.delete(i)
    for i in sub:
        db.session.delete(i)
    db.session.commit()

    # i is current user
    for i in range(1,11):
        arr = random.sample(range(1,11),random.randint(1,10))
        for j in arr:
            if i != j:
                sub = Subscribe(explorer=i,contributor=int(j))
                db.session.add(sub)
        arr = random.sample(range(1, 101),random.randint(1,100))
        for j in arr:
            a = str(datetime.now())
            date = int(a[0:10].replace("-",""))
            like = Like(explorer=i,recipe=int(j),date=date)
            db.session.add(like)
    db.session.commit()

# synchronize sum likes and daily likes
add_relation()
recipes = Recipes.query.all()
for r in recipes:
    r.sumlikes = int(Like.query.filter(Like.recipe == r.Rid).count())
    r.dailylikes = int(Like.query.filter(Like.recipe == r.Rid).count())

db.session.commit()
for i in range(1,11):
    totallikes = db.session.query(func.sum(Recipes.sumlikes))\
    .filter(Recipes.Uid==i).scalar()
    u = User.query.get(i)
    u.likes=totallikes
    db.session.add(u)
    db.session.commit()