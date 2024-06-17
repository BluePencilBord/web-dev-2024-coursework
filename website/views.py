from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .models import Recipe, Photo, Review
import os, hashlib, markdown, bleach
from . import decorators
from . import db

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def commit_recipe_data(request, id=None):
    title = request.form.get('title')
    description = bleach.clean(request.form.get('description'))
    time_to_cook = request.form.get('time_to_cook')

    if not all([title, time_to_cook, description != 'Описание процесса приготовления']):
        flash("Пожалуйста, введите все данные", category="error")
        return redirect(request.url)

    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            flash("Пожалуйста, введите все данные", category="error")
            return redirect(request.url)
        if file and allowed_file(file.filename):   
            file_md5 = hashlib.md5(file.read()).hexdigest() 
            filename = secure_filename(file.filename)
            try:
                photo = db.session.scalars(db.select(Photo).where(Photo.MD5_hash == file_md5)).one_or_none()
                if photo:
                    photo_id = photo.id
                else:
                    new_photo = Photo(file_name=filename, MIME_type=file.content_type, MD5_hash=file_md5)
                    db.session.add(new_photo)
                    db.session.flush() 
                    photo_id = new_photo.id
                new_recipe = Recipe(title=title, description=description, time_to_cook=time_to_cook, photo_id=photo_id)
                db.session.add(new_recipe)
                db.session.commit()
                recipe_id = new_recipe.id
                file.seek(0)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                return redirect(url_for('views.view_recipe', id=recipe_id))
            except Exception as e:
                db.session.rollback()
                flash(f"{e}", category="error")   
                return redirect(request.url)
    else:
        recipe = Recipe.query.get_or_404(id)
        recipe.title = request.form.get('title')
        recipe.description = bleach.clean(request.form.get('description'))
        recipe.time_to_cook = request.form.get('time_to_cook')
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", category="error")   
            return redirect(request.url)      

@views.route('/')
def home_page():
    recipes = Recipe.query

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    pages = recipes.paginate(page=page, per_page=8)

    return render_template("home.html", user=current_user, pages=pages)

@views.route('/add_recipe', methods=['GET', 'POST'])
@decorators.role_required('admin')
def add_recipe():                 
    if request.method == 'POST':
        return commit_recipe_data(request)

    return render_template("add_recipe.html", user=current_user, recipe=None)

@views.route('/view_recipe/<int:id>', methods=['GET', 'POST'])
@decorators.role_required('admin', 'mod', 'user')
def view_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    recipe.description = markdown.markdown(recipe.description)

    reviews = db.session.scalars(db.select(Review).where(Review.recipe_id == id)).all()
    user_reviewed = False

    for review in reviews:
        review.text = markdown.markdown(review.text)
        if review.user_id == current_user.id:
            user_reviewed = True

    return render_template("view_recipe.html", user=current_user, recipe=recipe, reviews=reviews, user_reviewed=user_reviewed)

@views.route('/edit_recipe/<id>', methods=['GET', 'POST'])
@decorators.role_required('admin', 'mod')
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)

    if request.method == 'POST':
        commit_recipe_data(request, id)
        return redirect(url_for('views.home_page'))
    else:
        return render_template("edit_recipe.html", user=current_user, recipe=recipe)

@views.route('/delete_recipe/<id>', methods=['GET', 'POST'])
@decorators.role_required('admin')
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)

    try:
        photo = recipe.photo
        photo_count = db.session.scalars(db.select(Recipe).where(photo.id == Recipe.cover_id)).all()
        db.session.delete(recipe)
        if photo and len(photo_count) == 1:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(photo)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error occured: {e}', category='error')

    return redirect(url_for('views.home_page'))

@views.route('/add_review/<id>', methods=['GET', 'POST'])
@decorators.role_required('admin', 'mod', 'user')
def add_review(id):
    recipe = Recipe.query.get_or_404(id)

    reviews = db.session.scalars(db.select(Review).where(Review.recipe_id == id)).all()

    for review in reviews:
        if review.user_id == current_user.id:
            flash('Вы уже оставляли отзыв', category='error')
            return redirect(url_for('views.home_page'))

    if request.method == 'POST':
        recipe_id = id
        user_id = current_user.id
        score = request.form.get('score')
        text = bleach.clean(request.form.get('text'))

        if text == 'Напишите свой отзыв': 
            flash("Пожалуйста, введите все данные", category="error")
            return redirect(request.url) 

        try:
            new_review = Review(recipe_id=recipe_id, user_id=user_id, score=score, text=text)
            db.session.add(new_review)
            db.session.commit()
            return redirect(url_for('views.view_recipe', id=recipe_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error occured: {e}', category='error')

    return render_template('add_review.html', user=current_user, recipe=recipe)