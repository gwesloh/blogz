from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import random
import string

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(10000000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_body, owner):
        self.blog_title = blog_title
        self.blog_body = blog_body
        self.id= request.args.get('id')
        self.owner = owner
    
    def __repr__(self):
        return '<Blog %r>' % self.blog_title
    
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(500))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)
        self.id= request.args.get('id')
    
    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        users = User.query.all()
        return render_template('index.html', users= users)
    else:
        users = User.query.all()
        return render_template('index.html', users= users)

@app.route('/blog', methods=['GET','POST'])
def get_blog():
    len_get= int(len(request.args))
    if (request.method == 'POST') or (len_get==0):
        posts = Blog.query.all()
        return render_template('blog.html', posts= posts)
    else:
        if "id" in request.args: 
            id= request.args.get('id')
            post= Blog.query.filter_by(id=id)
            blog_title =request.args.get('blog_title')
            blog_body = request.args.get('blog_body')
            return render_template('individ_post.html', blog_title= blog_title, blog_body= blog_body, post=post, id=id)
        elif "user" in request.args:
            userId=request.args.get('user')
            user= User.query.get(int(userId))
            blogs= user.blogs
            username= user.username
            return render_template('individ_user.html', blogs= blogs, username=username, userId=userId)
        else:
            posts = Blog.query.all()
            return render_template('blog.html', posts= posts)
       
@app.route('/newpost', methods=['GET','POST'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == 'POST':
        is_error= False
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        if not char_present(blog_title):
            flash('Please Enter a Title for your Blog', category= 'title_error')
            is_error= True
    
        if not char_present(blog_body):
            flash('Please Enter your Blog Post', category= 'body_error')
            is_error= True
        
        if is_error:
            return render_template('newpost.html')
        
        else:
            owner = User.query.filter_by(username=session['user']).first()
            new_post= Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()
            new_title= new_post.blog_title
            new_posts= Blog.query.filter_by(blog_title=new_title)
            
            return redirect ("/blog?id="+ str(new_post.id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if check_pw_hash(password, user.pw_hash):
                session['user'] = user.username
                flash('welcome back, ' + user.username)
                return redirect("/newpost")
            else:
                flash('Invalid Password', category= 'login_pw_error')
               
        else:
            flash('Invalid Username', category= 'login_error')
            
        return redirect("/login")

@app.route("/signup", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        is_error=False
        if not char_present(username):
            flash('oh no! Username field is blank', category= 'username_error')
            is_error= True
    
        if not char_present(password):
            flash('oh no! Password field is blank', category= 'password_error')
            is_error= True
    
        if not char_present(verify):
            flash('oh no! Verify field is blank', category= 'verify_error')
            is_error= True

        if not is_username_or_pass(username):
            flash('oh no! "' + username + '" does not seem like a username', category= 'username_error')
            is_error= True
        
        if not is_username_or_pass(password):
            flash('oh no! "' + password + '" does not seem like a password', category= 'password_error')
            is_error= True
        
        if password != verify:
            flash('passwords did not match', category= 'verify_error')
            is_error= True
        
        username_db_count = User.query.filter_by(username=username).count()
        
        if username_db_count > 0:
            flash('yikes! "' + username + '" is already taken')
            is_error= True

        if is_error:
            return render_template('signup.html', username= username)
        else:
            user = User(username=username, password=password) 
            db.session.add(user)
            db.session.commit()
            session['user'] = user.username
            return redirect("/newpost")
    else:
        return render_template('signup.html')


def is_username_or_pass(string):
    len_test_low = len(string) >= 3
    len_test_high = len(string) <= 20
    space_index = string.find(' ')
    space_present = space_index >=0
    if not len_test_low:
        return False
    elif not len_test_high:
        return False
    elif space_present:
        return False
    else:
        return True 



def char_present(string):
    char_is_present = len(string) != 0
    if not char_is_present:
        return False
    else:
        return True

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/blog")

endpoints_without_login = ['login', 'register','index','get_blog','/']

@app.before_request
def require_login():
    if not (('user' in session) or (request.endpoint in endpoints_without_login)):
        return redirect("/login")



def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])


def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0},{1}'.format(hash, salt)


def check_pw_hash(password, hash):
    salt = hash.split(',')[1]
    if make_pw_hash(password, salt) == hash:
        return True

    return False

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'
if __name__ == '__main__':
    app.run()