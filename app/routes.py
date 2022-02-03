from app import app
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegisterForm, LoginForm, ProductForm
from app.models import User, Product, Category


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/register', methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Get the data from the form
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if either the username or email is already in db
        user_exists = User.query.filter((User.username == username)|(User.email == email)).all()
        # if it is, return back to register
        if user_exists:
            flash(f"User with username {username} or email {email} already exists", "danger")
            return redirect(url_for('register'))
        # Create a new user instance using form data
        User(username=username, email=email, password=password)
        flash("Thank you for registering!", "primary")
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        
        # Grab the data from the form
        username = form.username.data
        password = form.password.data
       
        # Query user table for user with username
        user = User.query.filter_by(username=username).first()
        
        # if the user does not exist or the user has an incorrect password
        if not user or not user.check_password(password):
            # redirect to login page
            flash('That username and/or password is incorrect', 'danger')
            return redirect(url_for('login'))
        
        # if user does exist and correct password, log user in
        login_user(user)
        flash('You have succesfully logged in', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have successfully logged out", "secondary")
    return redirect(url_for('index'))


@app.route('/products/<int:prod_id>')
@login_required
def product_info(prod_id):
    product = Product.query.get_or_404(prod_id)
    return render_template('product.html', product=product)


@app.route('/products/<int:prod_id>/edit', methods=["GET", "POST"])
@login_required
def edit_product(prod_id):
    if not current_user.is_admin:
        flash("Excuse me, you are not allowed here.", "warning")
        return redirect(url_for('index'))
    product = Product.query.get_or_404(prod_id)
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        # Get data from form
        name = form.name.data
        price = form.price.data
        image_url = form.image_url.data
        cat_id = form.category_id.data

        # Update the product with the new info
        product.name = name
        product.price = price
        product.image_url = image_url
        product.category_id = cat_id

        product.save()

        # flash message
        flash(f"{product.name} has been updated", "primary")
        return redirect(url_for('product_info', prod_id=product.id))

    return render_template('edit_product.html', product=product, form=form)


@app.route('/products/<int:prod_id>/delete')
@login_required
def delete_product(prod_id):
    if not current_user.is_admin:
        flash("Excuse me, you are not allowed here.", "warning")
        return redirect(url_for('index'))
    product = Product.query.get_or_404(prod_id)
    product.delete()
    flash(f'{product.name} has been deleted', 'danger')
    return redirect(url_for('index'))
