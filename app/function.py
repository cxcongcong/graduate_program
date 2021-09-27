# functions for routes.py
from app import db
from app.models import User, Recipes, Like, Subscribe, Ingredient, StepDetail, Comment, typelog, methodlog
from sqlalchemy import func
import os
import cv2
from datetime import datetime
import heapq

basedir = os.path.abspath(os.path.dirname(__file__))

# pre-defined food type and cook method
food_type = ["breakfast and brunch", "lunch box", "dinner", "quick&easy", "vegan", "international food"
    , "baking", "healthy food", "drink", "dessert"]
cook_method = ["baking", "frying", "roasting", "grilling", "steaming", "poaching",
               "simmering", "broiling", "blanching", "braising", "stewing"]


# Input: login status and current user id
# Output: Top recipes and hot contributors
# Function: To get data to display the index page

def index_page(login_status, current_id):
    # add OP in likeopration
    users = User.query.order_by(User.likes.desc()).limit(20).all()  # change as no likes any more
    result = db.session.query(Recipes, User).filter(Recipes.Uid == User.Uid).order_by(Recipes.sumlikes.desc()).limit(
        10).all()
    recipe = []
    union_user = []
    for r, u in result:
        recipe.append(r)
        union_user.append(u)

    res = {"recipes": [], "contributor": [], "login": login_status}
    for recipe, u in zip(recipe, union_user):
        like_state = False
        if current_id:
            if (Like.query.filter(Like.recipe == recipe.Rid).filter(Like.explorer == current_id).first() != None):
                like_state = True
        temp = {"id": recipe.Rid,
                "title": recipe.name,
                "description": "",
                "author": u.id,
                "like": like_state,
                "totallikes": recipe.sumlikes,
                "src": "../../static/profile/recipe/" + str(recipe.Rid) + ".png"}
        res['recipes'].append(temp)
    for user in users:
        sub_state = False
        if current_id:
            if (Subscribe.query.filter(Subscribe.explorer == current_id).filter(
                    Subscribe.contributor == user.Uid).first() != None):
                sub_state = True
        temp = {"uid": user.Uid,
                "id": user.id,
                "src": "../../static/profile/user/" + str(user.Uid) + ".png",
                "substatus": sub_state}
        res['contributor'].append(temp)
    return res


# Input: siginup form from front end
# Output: This new user's Uid
# Function: receive sign up request and connect database to store data
def SignUp(form):
    user = User(id=form.id.data, email=form.email.data)
    user.set_password(form.password.data)
    user.likes = 0
    db.session.add(user)
    db.session.commit()
    basedir = os.path.abspath(os.path.dirname(__file__))
    path_read = basedir + "/static/profile/user/default_icon.png"
    path_write = basedir + "/static/profile/user/" + str(user.Uid) + ".png"
    img = cv2.imread(path_read)
    cv2.imwrite(path_write, img)
    return user.Uid


# Input: current user
# Output: Personal information for this user
# Function: Pass the personal information for user currently logged in
def getProfileInfomation(user):
    path = "../../static/profile/user/" + str(user.Uid) + ".png"
    totallikes = db.session.query(func.sum(Recipes.sumlikes)) \
        .filter(Recipes.Uid == user.Uid).scalar()
    if totallikes == None:
        totallikes = 0
    follower = str(Subscribe.query.filter(Subscribe.contributor == user.Uid).count())
    return {"uid": user.Uid,
            "id": user.id,
            "description": user.description,
            "email": user.email,
            "phone": user.phone,
            "totallikes": totallikes,
            "follower": follower,
            "src": path}


# Input: person profile form, current user, img_icon
# Output: current user's Uid
# Function: Receive updated personal profile form and update database accordingly, update avatar if needed
def UpdateProfile(form, current_user, img_icon):
    if img_icon.filename != '':
        basedir = os.path.abspath(os.path.dirname(__file__))
        path_write = basedir + "/static/profile/user/" + str(current_user.Uid) + ".png"
        img_icon.save(path_write)
    if form and current_user:
        current_user.id = form.id.data
        current_user.address = form.address.data
        current_user.phone = form.phone.data
        current_user.description = form.description.data
        db.session.commit()
    return current_user.Uid


# Input: current user
# Output: favorite recipes for this user
# Function: return this user's liked recipes
def getfavoriteRecipe(user):
    query_favorite = Like.query.filter(Like.explorer == user.Uid).all()
    favourite_recipes_rids = set()
    for query in query_favorite:
        favourite_recipes_rids.add(query.recipe)
    favoriterecipes = {"recipes": []}
    for rid in favourite_recipes_rids:
        recipe = Recipes.query.get(rid)
        if recipe:
            contributor = User.query.get(recipe.Uid)
            temp = {"id": recipe.Rid, "title": recipe.name, "description": recipe.description,
                    "author": contributor.id,
                    "like": "true", "totallikes": recipe.sumlikes,
                    "src": "../../static/profile/recipe/{}.png".format(recipe.Rid)}
            favoriterecipes["recipes"].append(temp)
    return favoriterecipes


# Input: current user
# Output: recipes the user posts
# Function: return this user's post recipes
def getPostRecipe(current_user):
    query_recipe = Recipes.query.filter(Recipes.Uid == current_user.Uid).all()
    postrecipes = {"recipes": []}
    for recipe in query_recipe:
        temp = {"id": recipe.Rid, "title": recipe.name, "description": recipe.description, "author": recipe.Uid,
                "like": "true", "totallikes": recipe.sumlikes,
                "src": "../../static/profile/recipe/{}.png".format(recipe.Rid)}
        postrecipes["recipes"].append(temp)
    return postrecipes


# Input: current user
# Output: favorite recipes for this user
# Function: return this user's liked recipes
def getSubscribePeople(current_user):
    query_subscribe = Subscribe.query.filter(Subscribe.explorer == current_user.Uid).all()
    user_uids = set()
    for query in query_subscribe:
        user_uids.add(query.contributor)
    subscribelist = {"subcribelist": []}
    for uid in user_uids:
        user = User.query.filter(User.Uid == uid).first()
        temp = {"uid": user.Uid, "id": user.id,
                "src": "../../static/profile/user/{}.png".format(user.Uid),
                "substatus": "true"}
        subscribelist["subcribelist"].append(temp)
    return subscribelist


# Input: recipe rid, current user uid
# Output: Details for this recipe, include type, method, ingredients, step, comments
# Function: return recipe detail
def getRecipeDetail(recipeid, cur_uid):
    recipe = Recipes.query.get(recipeid)
    contributor = User.query.get(recipe.Uid)
    # "ingredients":[{"name":"sugar","amount":"1/2cup"},{"name":"flour","amount":"1/2cup"}]
    ingredients = Ingredient.query.filter(Ingredient.recipe == recipeid).all()
    ingredients_list = []
    for i in range(len(ingredients)):
        ingredients_list.append({"name": ingredients[i].type, "amount": str(ingredients[i].weight)})
    # "steps":[{"step":"balabala"},{"step":"abb b balabala"}]
    steps = StepDetail.query.filter(StepDetail.recipe == recipeid).all()
    steps_list = []
    for i in range(len(steps)):
        steps_list.append({"step": steps[i].description})
    comments = Comment.query.filter(Comment.recipe == recipeid).all()
    comments_list = []
    for comment in comments:
        explorer_info = User.query.filter(User.Uid == comment.explorer).first()
        # "comments":[{"uid":12345,"id":"jeffy","src":"../../static/icons/girl_icon_1.png",
        #              "comment":"jiushi che shi er yi la ","committime":"132312"},
        #             {"uid":12345,"id":"EOcj","src":"../../static/icons/girl_icon_1.png",
        #             "comment":"jiushi che shi er yi la ","committime":"132312"}],
        temp = {"uid": explorer_info.Uid, "id": explorer_info.id,
                "src": "../../static/profile/user/{}.png".format(explorer_info.Uid),
                "comment": comment.content, "committime": comment.date}
        comments_list.append(temp)
    like_state = "false"
    if Like.query.filter(Like.recipe == recipeid).filter(Like.explorer == cur_uid).first() != None:
        like_state = "true"
    sub_state = "false"
    if Subscribe.query.filter(Subscribe.contributor == contributor.Uid) \
            .filter(Subscribe.explorer == cur_uid).first() != None:
        sub_state = "true"
    detail = {"contributoruid": contributor.Uid,
              "contributorid": contributor.id,
              "contributorsrc": "../../static/profile/user/{}.png".format(contributor.Uid),
              "title": recipe.name,
              "type": recipe.type,
              "method": recipe.method,
              "description": recipe.description,
              "pictures": "../../static/profile/recipe/{}.png".format(recipe.Rid),
              "ingredients": ingredients_list,
              "steps": steps_list,
              "comments": comments_list,
              "like": like_state,
              "subscribe": sub_state,
              "totallikes": recipe.sumlikes}
    return detail


# Input: current user uid, details for this recipe, include type, method, ingredients, step
# Output: recipe rid
# Function: store new uploaded recipe
def create_recipe(name, user_id, method, type, step_list, ingredients_name, ingredients_a, img_icon):
    a = str(datetime.now())
    date = int(a[0:10].replace("-", ""))
    time = int(a[11:19].replace(":", ""))
    r = Recipes(name=name, Uid=user_id, sumlikes=0, dailylikes=0, method=method,
                type=type, date=date, time=time, description="")
    db.session.add(r)
    db.session.commit()
    idx = 0
    for step in step_list:
        idx = idx + 1
        s = StepDetail(recipe=r.Rid, sequence=idx, description=step)
        db.session.add(s)
    db.session.commit()
    idx = 0
    for name, amount in zip(ingredients_name, ingredients_a):
        idx = idx + 1
        i = Ingredient(recipe=r.Rid, sequence=idx, type=name, weight=amount)
        db.session.add(i)
    db.session.commit()
    basedir = os.path.abspath(os.path.dirname(__file__))
    path_write = basedir + "/static/profile/recipe/" + str(r.Rid) + ".png"
    img_icon.save(path_write)
    return r.Rid


# Input: current user uid, details for this recipe, include type, method, ingredients, step
# Output: recipe rid
# Function: update old recipe
def update_recipe(recipeid, name, user_id, method, type, step_list, ingredients_name, ingredients_a, img_icon):
    r = Recipes.query.get(recipeid)
    db.session.delete(r)
    db.session.commit()

    steps = StepDetail.query.filter(StepDetail.recipe == recipeid)
    for s in steps:
        db.session.delete(s)
    db.session.commit()
    ins = Ingredient.query.filter(Ingredient.recipe == recipeid)
    for i in ins:
        db.session.delete(i)
    db.session.commit()

    a = str(datetime.now())
    date = int(a[0:10].replace("-", ""))
    time = int(a[11:19].replace(":", ""))
    r = Recipes(name=name, Uid=user_id, sumlikes=0, dailylikes=0, method=method,
                type=type, date=date, time=time)
    db.session.add(r)
    db.session.commit()
    idx = 0
    for step in step_list:
        idx = idx + 1
        s = StepDetail(recipe=r.Rid, sequence=idx, description=step)
        db.session.add(s)
    db.session.commit()
    idx = 0
    for name, amount in zip(ingredients_name, ingredients_a):
        idx = idx + 1
        i = Ingredient(recipe=r.Rid, sequence=idx, type=name, weight=amount)
        db.session.add(i)
    db.session.commit()
    if img_icon.filename != '':
        basedir = os.path.abspath(os.path.dirname(__file__))
        path_write = basedir + "/static/profile/recipe/" + str(r.Rid) + ".png"
        img_icon.save(path_write)
    return r.Rid

# Input: recipe rid, current user uid, comment
# Output: recipe rid
# Function: store new comment from the user to this recipe
def post_comment(rid, uid, comment):
    c = Comment(recipe=rid, explorer=uid, content=comment)
    db.session.add(c)
    db.session.commit()
    return rid


# Input: key words for searching recipes
# Output: all matched recipes
# Function: key word based search algorithm
def search_keyword(name, type, method, ingreidents, contributor, current_id):
    recipe = []
    user = []
    if ingreidents:
        query = db.session.query(Recipes, User, Ingredient).filter(Recipes.Uid == User.Uid,
                                                                   Recipes.Rid == Ingredient.recipe)
        query = query.filter(Ingredient.type.like("%{}%".format(ingreidents)))
        if name and name != '':
            query = query.filter(Recipes.name.like("%{}%".format(name)))
        if type and type != '':
            query = query.filter(Recipes.type.like("%{}%".format(type)))
        if method and method != '':
            query = query.filter(Recipes.method.like("%{}%".format(method)))
        if contributor and contributor != '':
            query = query.filter(User.id.like("%{}%".format(contributor)))
        query = query.all()
        for r, u, i in query:
            recipe.append(r)
            user.append(u)
    else:
        query = db.session.query(Recipes, User).filter(Recipes.Uid == User.Uid)
        if name and name != '':
            query = query.filter(Recipes.name.like("%{}%".format(name)))
        if type and type != '':
            query = query.filter(Recipes.type.like("%{}%".format(type)))
        if method and method != '':
            query = query.filter(Recipes.method.like("%{}%".format(method)))
        if contributor and contributor != '':
            query = query.filter(User.id.like("%{}%".format(contributor)))
        query = query.all()
        for r, u in query:
            recipe.append(r)
            user.append(u)
    recipe_data = {"recipes": []}
    dup = []
    for r, u in zip(recipe, user):
        if r not in dup:
            dup.append(r)
            like_state = "false"
            if (Like.query.filter(Like.recipe == r.Rid).filter(Like.explorer == current_id).first() != None):
                like_state = "true"
            temp = {"id": str(r.Rid), "title": r.name, "description": r.description,
                    "author": u.id, "like": like_state, "totallikes": str(r.sumlikes),
                    "src": "../../static/profile/recipe/{}.png".format(r.Rid)}
            recipe_data["recipes"].append(temp)
    return recipe_data


# Input: recipe rid
# Output: relevant recipes
# Function: recommend relevant recipes based on this recipe's ingredients
def getrelevant(recipeid):
    target_ingredients = set()
    temp = Ingredient.query.filter(Ingredient.recipe == recipeid).all()
    for ingredient in temp:
        target_ingredients.add(ingredient.type)
    # print(target_ingredients)
    result = []
    all_recipes = Recipes.query.all()
    for recipe in all_recipes:
        cur_rid = recipe.Rid
        if cur_rid != recipeid:
            cur_ingredients = set()
            temp = Ingredient.query.filter(Ingredient.recipe == cur_rid).all()
            for ingredient in temp:
                cur_ingredients.add(ingredient.type)
            same_ingredients = len(target_ingredients & cur_ingredients)
            heapq.heappush(result, (same_ingredients, cur_rid))
            if len(result) > 5:
                heapq.heappop(result)
    recipes = {"releventrecipes": []}
    for res in result:
        recipe = Recipes.query.get(res[1])
        temp = {"recipeid": recipe.Rid, "recipetitle": recipe.name,
                "src": "../../static/profile/recipe/{}.png".format(recipe.Rid)}
        recipes["releventrecipes"].append(temp)
    return recipes

# Input: current user uid
# Output: new recipes from his/her followed contributors
# Function: return new recipes for current user based on date, sum likes, time
def get_news(current_uid):
    result = db.session.query(Recipes, Subscribe).filter(Recipes.Uid == Subscribe.contributor,
                                                         Subscribe.explorer == current_uid). \
        order_by(Recipes.date.desc(), Recipes.sumlikes.desc(), Recipes.time.desc()).all()

    user = User.query.get(current_uid)
    totallikes = db.session.query(func.sum(Recipes.sumlikes)) \
        .filter(Recipes.Uid == user.Uid).scalar()
    if totallikes == None:
        totallikes = 0
    follower = str(Subscribe.query.filter(Subscribe.contributor == user.Uid).count())

    data = {"useruid": user.Uid, "userid": user.id, "usersrc": "../../static/profile/user/{}.png".format(user.Uid),
            "getlikes": totallikes, "getfollowers": follower, "recipes": []}
    for r, s in result:
        c_id = User.query.filter(User.Uid == r.Uid).first()
        like_state = "false"
        if (Like.query.filter(Like.recipe == r.Rid).filter(Like.explorer == current_uid).first() != None):
            like_state = "true"
        date = str(r.date)
        time = str(r.time)
        if len(time) == 5:
            time = "0" + time
        createtime = time[0:2] + ":" + time[2:4] + " " + date[4:6] + "/" + date[6:9] + "/" + date[0:4]
        temp = {"contributoruid": r.Uid, "contributorid": c_id.id,
                "contributorsrc": "../../static/profile/user/" + str(r.Uid) + ".png",
                "recipeid": r.Rid, "title": r.name, "like": like_state, "totallikes": str(r.sumlikes),
                "src": "../../static/profile/recipe/{}.png".format(r.Rid),
                "createtime": createtime
                }
        data["recipes"].append(temp)
    return data

# Input: detail from search key word
# Output: None
# Function: log the users' custom
def record_explore(detail):
    t = typelog.query.get(detail["type"])
    t.Number += 1
    m = methodlog.query.get(detail["method"])
    m.Number += 1
    db.session.commit()

# Input: None
# Output: food type and cook method
# Function: recommend food type and cook method based on users' custom
def cloud_pic():
    top_method = methodlog.query.order_by(methodlog.Number.desc()).limit(5).all()
    top_type = typelog.query.order_by(typelog.Number.desc()).limit(5).all()
    res = []
    for method in top_method:
        res.append(method.Name)
    for type in top_type:
        res.append(type.Name)
    return res


# Input: recipe rid
# Output: None
# Function: delete the recipe cascaded
def deleteRecipe(recipeid):
    r = Recipes.query.get(recipeid)
    db.session.delete(r)
    db.session.commit()
    steps = StepDetail.query.filter(StepDetail.recipe == recipeid)
    for s in steps:
        db.session.delete(s)
    db.session.commit()
    ins = Ingredient.query.filter(Ingredient.recipe == recipeid)
    for i in ins:
        db.session.delete(i)
    db.session.commit()
    comments = Comment.query.filter(Comment.recipe == recipeid)
    for c in comments:
        db.session.delete(c)
    db.session.commit()
    basedir = os.path.abspath(os.path.dirname(__file__))
    path_write = basedir + "/static/profile/recipe/" + str(recipeid) + ".png"
    if os.path.exists(path_write):
        os.remove(path_write)
