
from app.models import User, Recipes
from app import db
import cv2
from datetime import datetime
import json
from sqlalchemy.ext.declarative import DeclarativeMeta

'''
id = 'tian'
email = 't@qq.com'
password='car'
user = User.query.filter_by(email=email).first()
if user is not None:
    db.session.delete(user)
    db.session.commit()
user = register_fun(id,email,password,None)
print(user)
print(user.id,user.email)
user_login = login_fun('t@qq.com','car')
if user_login is None:
    print('invalid input')
else:
    print(user_login)
    print(user_login.id, user_login.email)
# image = read_avatar(user_login)
# cv2.imshow('avatar',image)
# cv2.waitKey(0)
recipes = index_info().get_recipe('sum')
for recipe in recipes:
    print(recipe.Rid, recipe.name, recipe.sumlikes, recipe.dailylikes, recipe.method, recipe.update_time)
print()
contributors = index_info().get_contributor()
for user in contributors:
    print(user.Uid, user.id, user.email, user.password, user.likes, user.phone)
print()
'''


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    if type(data) is datetime:
                        data = data.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)


def to_json(query):
    json_res = json.loads(json.dumps(query, cls=AlchemyEncoder))
    return json_res


user = User.query.all()
recipe = Recipes.query.all()
user_json, recipe_json = to_json(user), to_json(recipe)
print('user:', user_json)
print('recipe', recipe_json)
print()


def index_page(user_json, recipe_json):
    res = {"recipes": [], "contributor": [], "login": "true"}
    for recipe in recipe_json:
        temp = {"id": recipe['Rid'],
                "title": recipe['name'],
                "description": "",  # model的recipe没有这个属性
                "author": recipe['Uid'],  # 暂时先用Uid，等联合查询出来再改，下面所有author都一样
                "like": "true",
                "totallikes": recipe['sumlikes'],
                "src": ""}
        res['recipes'].append(temp)
    for user in user_json:
        temp = {"uid": user['Uid'],
                "id": user['id'],
                "src": "",
                "substate": "true"}
        res['contributor'].append(temp)
    return res


# format:
# {"recipes":[{"id": "", "title": "", "description": "", "author": "","like": "true","totallikes": "","src": ""}],
#  "contributor":[{"uid": "", "id": "", "src": "","substate":"true"}],
#  "login": "true"}
print(index_page(user_json, recipe_json))
print()


def getIndexInfo(user_json, recipe_json):
    res = {"recipes": [], "contributor": [], "login": "true"}
    for recipe in recipe_json:
        temp = {"id": recipe['Rid'],
                "title": recipe['name'],
                "description": "",  # model的recipe没有这个属性
                "author": recipe['Uid'],
                "like": "true",
                "totallikes": recipe['sumlikes'],
                "src": ""}
        res['recipes'].append(temp)
    for user in user_json:
        temp = {"uid": user['Uid'],
                "id": user['id'],
                "src": "", }
        res['contributor'].append(temp)
    return res


# format:
# {"recipes":[{"id": "", "title": "", "description": "", "author": "","like": "true","totallikes": "","src": ""}],
#  "contributor":[{"uid": "", "id": "", "src": ""}],
#  "login": "true"}
print(getIndexInfo(user_json, recipe_json))
print()


# profilepage传入单条query
def getProfileInfomation(user_json):
    return {"uid": user_json['Uid'],
            "id": user_json['id'],
            "description": user_json['description'],
            "email": user_json['email'],
            "phone": user_json['phone'],
            "src": ""}


# format:
# {"uid": "", "id": "", "description": "", "email": "", "phone": "", "src": ""}
print(getProfileInfomation(user_json[0]))
print()


def getfavoriterecipes(recipe_json):
    res = {"recipes": []}
    for recipe in recipe_json:
        temp = {"id": recipe['Rid'],
                "title": recipe['name'],
                "description": "",
                "author": recipe['Uid'],
                "like": "true",
                "totallikes": recipe['sumlikes'],
                "src": ""}
        res['recipes'].append(temp)
    return res


# format:
# {"recipes": [{"id": "", "title": "", "description": "",
#               "author": "", "like": "true", "totallikes": "", "src": ""},...]}
print(getfavoriterecipes(recipe_json))
print()


def getpostrecipes(recipe_json):
    return getfavoriterecipes(recipe_json)


# same as above

def getsubscribe(user_json):
    res = {"subscribelist": []}
    for user in user_json:
        temp = {"uid": user['Uid'], "id": user['id'], "src": "", "substate": "true"}
        res['subscribelist'].append(temp)
    return res


# format:
# {"subcribelist":[{"uid": "", "id": "", "src": "", "substate": "true"},....]}
print(getsubscribe(user_json))
print()
