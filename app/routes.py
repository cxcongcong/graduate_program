# This file is used to connect all back end functions with front end web
# Function detail can jump to function.py to look up
from flask import Flask, render_template, flash, redirect, request
from flask.helpers import url_for
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf import form
from app.models import User, Recipes, Subscribe, Like
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from werkzeug.urls import url_parse
from app import db
from flask import jsonify
from app.function import index_page, getProfileInfomation, getfavoriteRecipe
import cv2
import os
from datetime import datetime


##############################################index##############################################
# template index page

# This route will lead to the main page for our web
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        usersrc = "../../static/profile/user/{}.png".format(current_user.Uid)
        login_status = "true"
    else:
        usersrc = ""
        login_status = "false"
    return render_template('index.html', usersrc=usersrc, login_status=login_status)


# Interface :used to template "contributor list" and "recipes List" and get login state
# Data type : json
# Return Data format:{"recipes":[{"id": "", "title": "", "description": "", "author": "","like": "true","totallikes": "true","src": ""}],"contributor":[{"uid": "", "id": "", "src": "","substatus":"true"}],"login": "true"}
@app.route('/getIndexInfo')
def getIndexInfo():
    login_status = "false"
    current_id = None
    if current_user.is_authenticated:
        login_status = "true"
        current_id = current_user.Uid
    data_index = index_page(login_status, current_id)
    # print(data_index)
    return jsonify(data_index)


# Function: login
# Para: email password
@app.route('/login', methods=["POST"])
def login():
    form = LoginForm()
    if form:
        # check if email exist
        # and check pass word correct
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return render_template('error.html')
        login_user(user, remember=False)
        flash('Login successfully!')
        return render_template('error.html')
    flash('Sorry, login failed.')
    return render_template('error.html')


# Function: signup
# Para: id email password

from app.function import SignUp


@app.route('/signup', methods=["POST"])
def signup():
    form = RegistrationForm()
    email = form.email.data
    check_user = User.query.filter(User.email == email).first()
    if form and check_user is None:
        SignUp(form)
        flash('Congratulations, registered successfully! Please sign in')
        return render_template('error.html')
    flash('Sorry, this account already exists.')
    return render_template('error.html')


##############################################profile##############################################
# template profile page
# Para: subname-info :user frofile favorite: user favorite recipes;
@app.route('/profile/<subname>', methods=["GET", "POST"])
def profile(subname):
    if current_user.is_authenticated:
        usersrc = "../../static/profile/user/{}.png".format(current_user.Uid)
        login_status = "true"
    else:
        usersrc = ""
        login_status = "false"
    return render_template('profile.html', subname=subname, usersrc=usersrc, login_status=login_status)


# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


# Interface : get user info to template "my profile subpage"
# Data type : json
# Return Data format:{"uid": "", "id": "", "description": "", "email": "","phone": "","src": "","totallikes":"","follower":""}
@app.route('/getprofileinfo')
def getprofileinfo():
    # info = {"uid": "123456", "id": "tom", "description": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "email": "xxxx@gmail.com",
    #         "address":"kennedy","phone": "04444444", "src": "../../static/icons/girl_icon_1.png", "totallikes": "200", "follower": "100"}
    info = getProfileInfomation(current_user)
    return jsonify(info)


# Function: save user info
# Para: id- user name;description;email;phone;src;

from app.function import UpdateProfile


@app.route('/profile/saveprofileinfo', methods=["POST"])
def saveprofileinfo():
    form = EditProfileForm()
    img_icon = request.files.get('upload_profile_icon')
    UpdateProfile(form, current_user, img_icon)
    return redirect('/profile/info')


# Interface : get user's favorite list to template "my favorite subpage"
# Data type : json
# Return Data format: {"recipes": [{"id": "", "title": "", "description": "", "author": "","like": "true","totallikes": "","src": ""},...]}
@app.route('/getfavorite', methods=["GET", "POST"])
def getfavorite():
    # favoriterecipes = {"recipes": [{"id": "134", "title": "chiken", "description": "aaa", "author": "aaa",
    #                                  "like": "true", "totallikes": "100", "src": "../../static/icons/bake-5160388_640.jpg"}]}
    favoriterecipes = getfavoriteRecipe(current_user)
    return jsonify(favoriterecipes)


# Interface : get user's post list to template "my post subpage"
# Data type : json
# Return Data format: {"recipes": [{"id": "", "title": "", "description": "", "author": "","like": "true","totallikes": "","src": ""},...]}
from app.function import getPostRecipe


@app.route('/getposts', methods=["GET", "POST"])
def getposts():
    # postrecipes = {"recipes": [{"id": "134", "title": "chiken", "description": "aaa", "author": "aaa",
    #                             "like": "true", "totallikes": "100", "src": "../../static/icons/bake-5160388_640.jpg"}]}
    postrecipes = getPostRecipe(current_user)
    return jsonify(postrecipes)


# Interface : get user's subscribe list to template "my subscribe subpage"
# Data type : json
# Return Data format:{"subcribelist":[{"uid": "", "id": "", "src": "","substate":"true"},....]}
from app.function import getSubscribePeople


@app.route('/getsubscribe', methods=["GET", "POST"])
def getsubscribe():
    # subscribelist = {"subcribelist": [{"uid": "1", "id": "Asimov",
    #                                    "src": "../../static/icons/girl_icon_1.png", "substate": "true"},
    #                                   {"uid": "2", "id": "abc",
    #                                    "src": "../../static/icons/girl_icon_1.png", "substate": "true"}
    #                                   ]}
    subscribelist = getSubscribePeople(current_user)
    return jsonify(subscribelist)


##############################################recipe##############################################

# template recipe page
# Para: id-recipe id; src-user icon address;
@app.route('/recipe/<int:recipeid>', methods=["GET", "POST"])
def recipe(recipeid):
    if current_user.is_authenticated:
        usersrc = "../../static/profile/user/{}.png".format(current_user.Uid)
        login_status = "true"
    else:
        usersrc = ""
        login_status = "false"
    return render_template('recipe.html', recipeid=recipeid, usersrc=usersrc, login_status=login_status)


# Interface : get recipe detail
# Data type : json
# Para type :recipeid
# Return Data format:{"contributoruid":"","contributorid":"","contributorsrc":"",title": "", "type": "", "method": "", "description": "","pictures":[{"index0":"src"},{"index1":""}],"ingredients":[{"1":"name,amount"},{"2":""}],"steps":[{"1":"balabala"},{"2":""}],"comments":[{"uid":"","id":"","src":"","comment":"","committime":""},...],"like":"true","totallikes":"123"}

from app.function import getRecipeDetail, record_explore


@app.route('/getrecipedetail/<int:recipeid>', methods=["GET"])
def getrecipedetail(recipeid):
    # testdetail = {
    # "contributoruid":12345,
    # "contributorid":"Tom",
    # "contributorsrc":"../../static/icons/girl_icon_1.png",
    # "title": "Fired chiken",
    #  "type": "",
    #  "method": "",
    #  "description": "This test demo",
    #  "pictures":"",
    #  "ingredients":[{"name":"sugar","amount":"1/2cup"},{"name":"flour","amount":"1/2cup"}],
    #  "steps":[{"step":"balabala"},{"step":"abb b balabala"}],
    #  "comments":[{"uid":12345,"id":"jeffy","src":"../../static/icons/girl_icon_1.png","comment":"jiushi che shi er yi la ","committime":"132312"},{"uid":12345,"id":"EOcj","src":"../../static/icons/girl_icon_1.png","comment":"jiushi che shi er yi la ","committime":"132312"}],
    #  "like": True,
    #  "subscribe":True,
    #  "totallikes":127}
    if current_user.is_authenticated:
        detail = getRecipeDetail(recipeid, current_user.Uid)
    else:
        detail = getRecipeDetail(recipeid, 0)
    # print(detail)
    record_explore(detail)
    return jsonify(detail)


# Interface : get relevent recipes
# Data type : json
# Para type :recipeid
# Return Data format:{"releventrecipes":[{"recipeid":"","recipetitle":"","src":""}]}
from app.function import getrelevant


@app.route('/releventrecipes/<int:recipeid>', methods=["GET"])
def releventrecipes(recipeid):
    recipes = getrelevant(recipeid)
    # testrecipe= {"releventrecipes":[{"recipeid":32,"recipetitle":"fffffffff","src":"../../static/icons/cake.jpg"},
    #                                {"recipeid":62,"recipetitle":"hhhhh","src":"../../static/icons/meat.jpg"},
    #                                {"recipeid":72,"recipetitle":"zzz","src":"../../static/icons/cake.jpg"},
    #                                {"recipeid":39,"recipetitle":"ddd","src":"../../static/icons/vegetables-5907330_1920.jpg"}]}
    return jsonify(recipes)


# Function: comment
# Para:recipeid-recipe id; comment-user conmment
from app.function import post_comment


@app.route('/comment', methods=["POST"])
def comment():
    form = request.form
    recipeid = form.get("recipeid")
    content = form.get("comment")
    post_comment(recipeid, current_user.Uid, content)
    return redirect(url_for('recipe', recipeid=recipeid))


##############################################create&edit recipe##################################
# template editrecipe page 
# Para:  recipeid; 
@app.route('/editrecipe/<int:recipeid>', methods=["GET"])
def editrecipe(recipeid):
    if current_user.is_authenticated:
        usersrc = "../../static/profile/user/{}.png".format(current_user.Uid)
        login_status = "true"
    else:
        usersrc = ""
        login_status = "false"
    return render_template('editrecipe.html', recipeid=recipeid, usersrc=usersrc, login_status=login_status)


# Function: save recipe
# Para: recipeid-if exist then update; title-recipe title; type -meal type; method; description; pictures; ingredients; steps;
# Post Data format:{"recipeid":"","title": "", "type": "", "method": "", "description": "","pictures":[{"index0":"src"},{"index1":""}],"ingredients":[{"1":"name,amount"},{"2":""}],"steps":[{"1":"balabala"},{"2":""}]}
from app.function import create_recipe, update_recipe


@app.route('/saverecipe/<int:recipeid>', methods=["POST"])
def saverecipe(recipeid):
    # form
    form = request.form
    # if id = 0 create others edit
    name = request.form.get('title')
    method = request.form.get('method')
    type = request.form.get('type')
    step_list = request.form.getlist('steps[]')
    img_icon = request.files.get('upload_picture')
    ingredients_name = request.form.getlist('ingredients_name[]')
    ingredients_a = request.form.getlist('ingredients_amount[]')
    if recipeid == 0:
        recipeid = create_recipe(name, current_user.Uid, method, type, step_list, ingredients_name, ingredients_a,
                                 img_icon)
    else:
        recipeid = update_recipe(recipeid, name, current_user.Uid, method, type, step_list, ingredients_name,
                                 ingredients_a, img_icon)
    return redirect(url_for('recipe', recipeid=recipeid))


# Function: delete recipe
# Para: recipeid
from app.function import deleteRecipe


@app.route('/deleterecipe/<int:recipeid>', methods=["POST"])
def deleterecipe(recipeid):
    deleteRecipe(recipeid)
    return redirect(url_for('profile', subname="post"))


##############################################search##############################################


# template search page
# Para:  keywords-in searchbox; type-meal type;
from app.function import search_keyword


@app.route('/search', methods=['GET', 'POST'])
def search():
    keyword = request.args.get('keyword')
    type = request.args.get('type')
    method = request.args.get('method')
    ingredients = request.args.get('ingredients')
    contributor = request.args.get('contributor')

    if current_user.is_authenticated:
        usersrc = "../../static/profile/user/{}.png".format(current_user.Uid)
        login_status = "true"
        recipe_data = search_keyword(keyword, type, method, ingredients, contributor, current_user.Uid)
    else:
        usersrc = ""
        login_status = "false"
        recipe_data = search_keyword(keyword, type, method, ingredients, contributor, 0)

    return render_template('search.html', usersrc=usersrc, login_status=login_status, recipes=recipe_data["recipes"])


from app.function import cloud_pic


@app.route('/getcloudpic', methods=['GET'])
def getcloudpic():
    # data = [
    #     'Meat',
    #     'Breakfast',
    #     'Juice',
    #     'Lunch',
    #     'Banana',
    #     'Cake',
    #     'Mr.D',
    #     'Rice',
    # ]
    data = cloud_pic()
    return jsonify(data)


##############################################news################################################
# template news page

@app.route('/news', methods=['GET', 'POST'])
def news():
    # if pageindx= 0 get totalnum of results and get page one otherwise get corresponding index page
    if current_user.is_authenticated:
        usersrc = "../../static/profile/user/{}.png".format(current_user.Uid)
        login_status = "true"
    else:
        usersrc = ""
        login_status = "false"
    return render_template('news.html', usersrc=usersrc, login_status=login_status)


# Interface : show subscribed contributor's posts
# Data type : json
# Para: pageindex-paging index
# Return Data format: {"newsList": [{"contributoruid":"","contributorid":"","contributorsrc":"","recipeid": "", "title": "","like": "true","totallikes": "","src": ""},...]}
from app.function import get_news


@app.route('/getnews', methods=['GET', 'POST'])
def getnews():
    # if pageindx= 0 get totalnum of results and get page one otherwise get corresponding index page
    #   data={"useruid":"123","userid":"annie","usersrc":"../../static/icons/girl_icon_1.png","getlikes":"123", "getfollowers":"500",
    #   "recipes":[{"contributoruid":"11","contributorid":"joe","contributorsrc":"../../static/icons/girl_icon_1.png","recipeid": "2", "title": "apple","like": "true","totallikes": "123","src": "../../static/profile/recipe/2.png","createtime":"20:47 17/6/2021"},
    #               {"contributoruid":"12","contributorid":"joshua","contributorsrc":"../../static/icons/girl_icon_1.png","recipeid": "3", "title": "chicken","like": "true","totallikes": "123","src": "../../static/profile/recipe/2.png","createtime":"20:47 15/6/2021"},
    #               {"contributoruid":"12","contributorid":"joshua","contributorsrc":"../../static/icons/girl_icon_1.png","recipeid": "3", "title": "chicken","like": "true","totallikes": "123","src": "../../static/profile/recipe/2.png","createtime":"20:47 15/6/2021"},
    #               {"contributoruid":"12","contributorid":"joshua","contributorsrc":"../../static/icons/girl_icon_1.png","recipeid": "3", "title": "chicken","like": "true","totallikes": "123","src": "../../static/profile/recipe/2.png","createtime":"20:47 15/6/2021"},
    #               {"contributoruid":"12","contributorid":"joshua","contributorsrc":"../../static/icons/girl_icon_1.png","recipeid": "3", "title": "chicken","like": "true","totallikes": "123","src": "../../static/profile/recipe/2.png","createtime":"20:47 15/6/2021"},
    #
    # ]}
    data = get_news(current_user.Uid)
    return jsonify(data)


##############################################common function######################################
# Function: like or cancel like
# Para:  likeop-1 like 0 cancle like;recipeid-recipe id;
@app.route('/likeopration/<int:likeop>/<int:recipeid>', methods=["POST"])
def likeopration(likeop, recipeid):
    if current_user.is_authenticated:
        a = str(datetime.now())
        cur_date = int(a[0:10].replace("-", ""))
        if likeop == 1:
            like = Like(explorer=current_user.Uid, recipe=recipeid)
            db.session.add(like)
            r = Recipes.query.get(recipeid)
            r.sumlikes += 1
            r.dailylikes += 1
            u = User.query.filter(User.Uid == r.Uid).first()
            u.likes += 1
            db.session.commit()
        elif likeop == 0:
            like = Like.query.filter(Like.explorer == current_user.Uid, Like.recipe == recipeid)[0]
            db.session.delete(like)
            r = Recipes.query.get(recipeid)
            r.sumlikes -= 1
            if like.date == cur_date: 
                r.dailylikes -= 1
            u = User.query.filter(User.Uid == r.Uid).first()
            u.likes -= 1
            db.session.commit()
        return ""
    else:
        return "not log in"


# Function: subscribe or unsubscribe
# Para:  subscribeop-1 subscribe 0 unsubscribe;recipeid-recipe id;
@app.route('/subscribeopration/<int:subscribeop>/<int:contributorid>', methods=["POST"])
def subscribeopration(subscribeop, contributorid):
    if current_user.is_authenticated:
        if subscribeop == 1:
            new_subscribe = Subscribe(contributor=contributorid, explorer=current_user.Uid)
            db.session.add(new_subscribe)
            db.session.commit()
        elif subscribeop == 0:
            old_subscribe = Subscribe.query.filter(Subscribe.contributor == contributorid,
                                                   Subscribe.explorer == current_user.Uid).first()
            db.session.delete(old_subscribe)
            db.session.commit()
        return ""
    else:
        return "not log in"
