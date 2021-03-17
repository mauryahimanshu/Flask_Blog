import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, ProfileUpdateForm, PostForm
from flaskblog import app, bcrypt, db
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', title='Home', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hash_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been successfully created! You may login now.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                formatted_next_page = next_page[1:]
                return redirect(url_for(formatted_next_page))
            else:
                return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form, title='Login')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


def save_image(form_image):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_image.filename)
    image_file_name = random_hex+f_ext
    image_path = os.path.join(app.root_path, 'static/profile_pics', image_file_name)

    output_size = (500, 500)
    resized_image = Image.open(form_image)
    resized_image.thumbnail(output_size)
    resized_image.save(image_path)

    return image_file_name

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = ProfileUpdateForm()
    if form.validate_on_submit():
        if current_user.username==form.username.data and current_user.email==form.email.data and form.image.data==None:
            flash('No change found!', 'info')
            return redirect(url_for('account'))
        if form.image.data:
            image_file_name = save_image(form.image.data)
            if current_user.image_file != 'default.jpg':
                image_path_delete = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
                os.remove(image_path_delete)
            current_user.image_file = image_file_name
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'profile_pics/{ current_user.image_file}')
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form, title='New Post', legend='New Post')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post, title='Post')


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post has been updated.', 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update Post', form = form, legend='Update')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been deleted', 'success')
    return redirect(url_for('index'))