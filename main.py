from flask import Flask,request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(10000000))

    def __init__(self, blog_title, blog_body):
        self.blog_title = blog_title
        self.blog_body = blog_body
        self.id= request.args.get('id')
        
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        posts = Blog.query.all()
        return render_template('blog.html', posts= posts)
    elif request.method == 'POST':
        posts = Blog.query.all()
        return render_template('blog.html', posts= posts)

@app.route('/blog', methods=['GET','POST'])
def get_post():
    if request.method == 'GET':
        id= request.args.get('id')
        post= Blog.query.filter_by(id=id)
        blog_title =request.args.get('blog_title')
        blog_body = request.args.get('blog_body')
        return render_template('individ_post.html', blog_title= blog_title, blog_body= blog_body, post=post, id=id)
    else:
        id= request.args.get('id')
        post= Blog.query.filter_by(id=id)
        blog_title =request.args.get('blog_title')
        blog_body = request.args.get('blog_body')
        return render_template('individ_post.html', blog_title= blog_title, blog_body= blog_body, post=post, id=id)


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
            new_post= Blog(blog_title, blog_body)
            db.session.add(new_post)
            db.session.commit()
            new_title= new_post.blog_title
            new_posts= Blog.query.filter_by(blog_title=new_title)
            
            return redirect ("/blog?id="+ str(new_post.id))
            



def char_present(string):
    char_is_present = len(string) != 0
    if not char_is_present:
        return False
    else:
        return True

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'
if __name__ == '__main__':
    app.run()