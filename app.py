from flask import Flask, render_template, request, redirect, url_for, g, flash, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from FDataBase import FDataBase
import os
import re
import sqlite3
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm


DATABASE = '/tmp/flblog.db'
DEBUG = True
SECRET_KEY = 'c289e5ace89efcecbb6be9f17eaa4045ad3591b8'
MAX_CONTENT_LENGTH = 1024*1024


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flblog.db')))


login_manager =  LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sql_db.sql', mode='r') as f:
        db.cursor().execute(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()




def get_date(sort):
    get_post = dbase.getPostsAnonce(sort)
    posts = []
    for p in get_post: 
        elem = dict(p)
        date_object = datetime.strptime(elem['date'], "%Y-%m-%d")
        formatted_date = date_object.strftime("%a %b %d %Y")
        elem['date'] = formatted_date
        posts.append(elem)
    return posts


@app.route('/')
def index():
    return render_template('index.html', posts = get_date({'sort' : 'default'}), tags = dbase.getTags(), title = 'Main', select_sort = 'default')

@app.route('/sort_by/<string:sort>')
def sort_by(sort):
    return render_template('index.html', posts = get_date({'sort' : sort}), tags = dbase.getTags(), title = 'Main', select_sort=sort)

@app.route('/tags/<string:tag>')
def sort_by_tags(tag):
    return render_template('index.html', posts = get_date({'tag' : tag}), tags = dbase.getTags(), title = 'Main', select_tags=tag, select_sort = 'default')

@app.route('/search', methods = ['POST', 'GET'])
def search():
    posts = None
    if request.method == 'POST':
        get_post = dbase.getPostsAnoncSearch(request.form['title_search'])
        posts = []
        for p in get_post: 
            elem = dict(p)
            date_object = datetime.strptime(elem['date'], "%Y-%m-%d")
            formatted_date = date_object.strftime("%a %b %d %Y")
            elem['date'] = formatted_date
            posts.append(elem)
    return render_template('index.html', posts = posts, tags = dbase.getTags(), title = 'Main', select_sort = 'default')





@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))
    
    return render_template('login.html', menu=dbase.getMenu(), form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('success')
    return redirect(url_for('login'))

@app.route('/register', methods = ['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_psw = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, hash_psw, datetime.now().date())
        if res: 
            # flash('success')
            return redirect(url_for('login'))
        # else:
            # flash('error')
    return render_template('register.html', menu=dbase.getMenu(), form=form)


@app.route('/profile')
@login_required
def profile():
    my_posts = dbase.getMyPosts(current_user.get_id())
    return render_template('profile.html', menu=dbase.getMenu(), my_posts=my_posts)






@app.route('/change_info', methods = ['POST', 'GET'])
@login_required
def change_info():
    if request.method == 'POST':
        res = dbase.updateUserInfo(current_user.get_id(), request.form['name'], request.form['email'])
        if res:
            flash('success')
        else:
            flash('error')
    return redirect(url_for('profile'))

@app.route('/userava')
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ''
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@app.route('/post_img/<int:post_id>')
def post_img(post_id):
    img_data = dbase.getImg(post_id)
    if not img_data:
        return ''
    response = make_response(img_data)
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route('/post_userava/<int:user_id>')
def post_userava(user_id):
    img_data = dbase.getAva(user_id)
    if not img_data:
        return ''
    response = make_response(img_data)
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route('/edit_post<int:post_id>', methods=['POST', 'GET'])
def edit_post(post_id):
    if request.method == 'POST':
        file = request.files['file_post']
        if file:
            if current_user.verifyExt(file.filename):
                try:
                    img = file.read()
                except FileNotFoundError as e:
                    print(e)
            else:
                flash('error, MUST BE PNG')
                return redirect(url_for('edit_post'))
        else:
            img = None        
        upd = dbase.updatePostInfo(post_id, request.form['title'], request.form['content'], img)
        if upd:
            flash('success')
        else:
            flash('error')       

    res = dbase.getPost(post_id)
    return render_template('edit_post.html', menu=dbase.getMenu(), post=res)



@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method == "POST":

        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if res:
                    flash('update')
                else:
                    flash('error')

            except FileNotFoundError as e:
                print(e)
        else:
            print('error55')
    return redirect(url_for('profile'))






    
@app.route('/add_post', methods = ['POST', 'GET'])
@login_required
def add_post():
    if request.method == 'POST':
        file = request.files['file_post']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
            except FileNotFoundError as e:
                print(e)
        else:
            flash('error, MUST BE PNG')
            return redirect(url_for('add_post'))
        
        tags = re.findall(r'\w+', request.form['tags'])

        res = dbase.addPost(current_user.get_id(), request.form['name'], request.form['text'], tags , img, datetime.now().date())

        if not res:
            flash('error')
        else:
            flash('success')

    return render_template('add_post.html', menu = dbase.getMenu())

@app.route('/add_comments/<int:post_id>', methods = ['POST', 'GET'])
@login_required
def add_comments(post_id):
    if request.method == 'POST':
        res = dbase.addComment(current_user.get_id(), post_id, request.form['comment'], datetime.now().date())
        if res:
            flash('success')
        else:
            flash('error')

        
    return redirect(url_for('show_post', post_id=post_id))
        




@app.route('/post/<int:post_id>')
@login_required
def show_post(post_id):
    res = dbase.getPost(post_id)
    comments = dbase.getComments(post_id)
    return render_template('post.html', menu = dbase.getMenu(), post_id=post_id, res=res, coms=comments)





if __name__ == '__main__':
    app.run(debug=True, port=8080)


                