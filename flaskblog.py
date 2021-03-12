from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

# Obtained via 'secrets' module , using token_hex(32) method, can use token_urlsafe(32)
app.config['SECRET_KEY'] = 'aeb76d8fed384db32cb23dff35e5a10587b64b7e0e5c5363ef35f3f5a23b5af9'

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for { form.username.data }!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form, title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@gmail.com' and form.password.data == 'password':
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('index'))
        else :
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form, title='Login')


if __name__ == '__main__':
    app.run(debug=True)