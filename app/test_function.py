
from app.models  import User, Recipes,Like,Subscribe,Comment
from app import db
from sqlalchemy import func,distinct
import cv2
from datetime import datetime
from app.function import index_page
import os
import random

def initial_img():
    basedir = os.path.abspath(os.path.dirname(__file__))
    path_read = basedir + "/static/icons/1.png"
    img = cv2.imread(path_read)
    for i in range(1,11):
        path_write = basedir + "/static/profile/user/" + str(i) + ".png"
        cv2.imwrite(path_write, img)

# initial_img()

from app.models  import Ingredient,StepDetail
def create_recipe(name,user_id,method,type,step_list,ingredients_name,ingredients_a):
    a = str(datetime.now())
    date = int(a[0:10].replace("-", ""))
    time = int(a[11:19].replace(":", ""))
    r = Recipes(name=name, Uid=user_id, sumlikes=0, dailylikes=0, method=method,
                type=type,date=date, time=time)
    db.session.add(r)
    db.session.commit()
    idx = 0
    for step in step_list:
        idx = idx+1
        s = StepDetail(recipe=r.Rid,sequence=idx,description=step)
        db.session.add(s)
    db.session.commit()
    idx = 0
    for name,amount in zip(ingredients_name,ingredients_a):
        idx = idx + 1
        i = Ingredient(recipe=r.Rid,sequence=idx,type=name,weight=amount)
        db.session.add(i)
    db.session.commit()


from app.function import search_keyword


name="test food"
user_id = 1
method="123"
type = "1234"
step_list =["clean","cook1","cook2"]
ingredients_name=["meat","vege","c"]
ingredients_a=["300g","3"]
# create_recipe(name,user_id,method,type,step_list,ingredients_name,ingredients_a)
print("success")

name = ''
method='simmering'
type = ''
ingreidents=''
contributor=''
# result = search_keyword(name,type,method,ingreidents,contributor,0)


def get_news(current_uid):
    result = db.session.query(Recipes,Subscribe).filter(Recipes.Uid==Subscribe.contributor,Subscribe.explorer==current_uid).\
     order_by(Recipes.date.desc(),Recipes.sumlikes.desc(),Recipes.time.desc()).all()
    data={"newsList":[]}
    for r,s in result:
        c_id=User.query.filter(User.Uid==r.Uid).first()
        like_state = "false"
        if (Like.query.filter(Like.recipe == r.Rid).filter(Like.explorer == current_uid).first() != None):
            like_state = "true"
        temp={"contributoruid":r.Uid,"contributorid":c_id,"contributorsrc":"../../static/profile/user/"+str(r.Uid)+".png",
              "recipeid":r.Rid,"title":r.name,"like":like_state,"totallikes":str(r.sumlikes),"src":"../../static/profile/recipe/{}.png".format(r.Rid)

        }
        data["newsList"].append(temp)
    return data

def post_comment(rid,uid,comment):
    c = Comment(recipe=rid,explorer=uid,content=comment)
    db.session.add(c)
    db.session.commit()

# post_comment(1,1,"This is the first comment")

recipe = Recipes.query.all()
for r in recipe:
    r.method = r.method.lower()
    r.type = r.type.lower()
db.session.commit()

result = db.session.query(Recipes.method,func.count(Recipes.method)).group_by(Recipes.method).all()


food_type = ["breakfast and brunch", "lunch box", "dinner", "quick&easy", "vegan", "international food"
    , "baking", "healthy food", "drink", "dessert"]
cook_method = ["baking","frying","roasting","grilling","steaming","poaching",
               "simmering","broiling","blanching","braising","stewing"]

# recipes = Recipes.query.all()
# for r  in recipes:
#     r.type=food_type[random.randint(0,9)]
# db.session.commit()

from app.models import typelog,methodlog
def update_log():
    types = typelog.query.all()
    methods = methodlog.query.all()
    for t in types:
        db.session.delete(t)
    for m in methods:
        db.session.delete(m)
    db.session.commit()

    for f in food_type:
        t = typelog(Name=f,Number=random.randint(0,100))
        db.session.add(t)
    for c in cook_method:
        t = methodlog(Name=c, Number=random.randint(0, 100))
        db.session.add(t)
    db.session.commit()