from crypt import methods
from app import app, db
from flask import render_template, flash, redirect, url_for, request, jsonify
from app.forms import LoginForm, RegistrationForm, InputValueForm
from flask_login import current_user, login_user, logout_user, login_required, user_logged_in
from app.models import Users, Values, Categories
from werkzeug.urls import url_parse


#* Listening on index page
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = Users.query.filter_by(username=current_user.username).first()
    all_categories = Categories.query.filter_by(user_id=user.id).all()
    category_ids = []
    values = []
    categories_count = []
    id = 'index'
    values_count = 0

    # Adding all categories and category_ids to lists
    for category in all_categories:
        category_ids.append(category.category_id)
        categories_count.append(Values.query.filter_by(category_id=category.category_id).count())
    
    # Adding values to list
    for value in category_ids:
        if id == 'index':
            temp_value = Values.query.filter_by(category_id=value).all()
        else:
            temp_value = Values.query.all()
        if temp_value:
            values = values + list(temp_value)
            values_count = len(values)

    
    form = InputValueForm()
    # When submit happens in value form
    if form.validate_on_submit():
        new_value = Values(title=form.title.data, value=form.value.data,
                                  category_id=form.category.data.category_id)
        db.session.add(new_value)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('index.html', title='Home', form=form, categories=all_categories,
                           values=values, categories_count=categories_count, categories_len=len(categories_count),
                           values_count=values_count)


#* Listening on login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already authenticated send to index page, else load login page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form2 = LoginForm()

    # When log in button is pressed
    if form2.validate_on_submit():
        user = Users.query.filter_by(username=form2.username.data).first()

        #If username does not exist or the password is incorrect try again
        if user is None or not user.check_password(form2.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form2, current_user=current_user)


#* Listening on register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already authenticated send to index page, else load register page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()

    # When register button is pressed add new user to db
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        user = Users.query.filter_by(username=form.username.data).first()
        categories = ['Car', 'Shopping', 'Girlfriend', 'Dates', 'School', 'Training', 'Work', 'Personal data']
        
        for c in categories:
            entry = Categories(c, user_id=user.id)
            db.session.add(entry)
        
        db.session.commit()
        flash('Successful registration!')
        
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Registration', form=form)


#* Logout listener
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#* Listener for categories
@app.route('/category')
@login_required
def category():
    id = request.args.get('id', None)
    id2 = request.args.get('id2', None)

    # Get current user and his items
    user = Users.query.filter_by(username=current_user.username).first()
    all_categories = Categories.query.filter_by(user_id=user.id).all()
    category_ids = []
    values = Values.query.filter_by(category_id=id).all()
    categories_count = []
    values_count = 0

    # Calculate for category sidenav
    for category in all_categories:
        category_ids.append(category.category_id)
        categories_count.append(Values.query.filter_by(category_id=category.category_id).count())
    for id in category_ids:
        values_count += Values.query.filter_by(category_id=id).count()

    # Value form
    form = InputValueForm()
    if form.validate_on_submit():
        new_value = Values(title=form.title.data, value=form.value.data,
                                  category_id=form.category.data.category_id)
        db.session.add(new_value)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('index.html', title='Home', form=form, categories=all_categories,
                           values=values, categories_count=categories_count, category_len=len(categories_count),
                           values_count=values_count)


#* Listener for values
@app.route('/value')
@login_required
def value():
    id = request.args.get('id', None)
    id2 = request.args.get('id2', None)

    # Load current user and his items
    user = Users.query.filter_by(username=current_user.username).first()
    all_categories = Categories.query.filter_by(user_id=user.id).all()
    category_ids = []
    categories_count = []
    values_count = 0
    chosen_value = Values.query.filter_by(value_id=id2).first()

    #? Neco kaj dfk je to
    if id is not None:
        values = Values.query.all()
    else:
        values = Values.query.all()

    # Calculate for category sidenav
    for category in all_categories:
        category_ids.append(category.category_id)
        categories_count.append(Values.query.filter_by(category_id=category.category_id).count())
    for id in category_ids:
        values_count += Values.query.filter_by(category_id=id).count()

    # Iput form
    form = InputValueForm()
    if form.validate_on_submit():
        new_value = Values(title=form.title.data, value=form.value.data,
                                  category_id=form.category.data.category_id)
        db.session.add(new_value)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('value.html', title='Home', form=form, categories=all_categories,
                           values=values, categories_count=categories_count, categories_len=len(categories_count),
                           values_count=values_count, chosen_value=chosen_value)