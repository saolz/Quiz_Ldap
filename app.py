from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from ldap_utils import get_user_details, authenticate_user
from config import Config
from models import db, Quiz, Response
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User:
    def __init__(self, username):
        self.username = username
        self.details = get_user_details(username)
        logger.debug(f"User details for {username}: {self.details}")

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(username):
    return User(username)

def has_attempted_quiz(username):
    return Response.query.filter_by(user=username).first() is not None

def calculate_user_score(username):
    responses = Response.query.filter_by(user=username).all()
    score = 0
    for response in responses:
        question = Quiz.query.get(response.question_id)
        if question and question.correct_option == response.selected_option:
            score += 1
    return score

@app.route('/')
@login_required
def home():
    is_admin = current_user.username.lower() == 'admin'
    show_quiz_button = current_user.details and current_user.details.get('ou') == 'Mumbai' and not has_attempted_quiz(current_user.username)
    quiz_attempted = has_attempted_quiz(current_user.username)
    flash_messages = session.pop('flash_messages', [])
    return render_template('home.html', user=current_user, show_quiz_button=show_quiz_button, is_admin=is_admin, quiz_attempted=quiz_attempted, flash_messages=flash_messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if current_user.username.lower() != 'admin':
        session['flash_messages'] = ['Only admin can create quizzes.']
        return redirect(url_for('home'))

    if request.method == 'POST':
        new_quiz = Quiz(
            question=request.form['question'],
            option1=request.form['option1'],
            option2=request.form['option2'],
            option3=request.form['option3'],
            option4=request.form['option4'],
            correct_option=int(request.form['correct_option'])
        )
        db.session.add(new_quiz)
        db.session.commit()
        session['flash_messages'] = ['Quiz question created successfully!']
        return redirect(url_for('create_quiz'))

    questions = Quiz.query.all()
    return render_template('create_quiz.html', questions=questions)

@app.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if current_user.username.lower() != 'admin':
        session['flash_messages'] = ['Only admin can delete questions.']
        return redirect(url_for('home'))

    question = Quiz.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    session['flash_messages'] = ['Question deleted successfully!']
    return redirect(url_for('create_quiz'))

@app.route('/take_quiz', methods=['GET', 'POST'])
@login_required
def take_quiz():
    if current_user.details['ou'] != 'Mumbai':
        session['flash_messages'] = ['Only users from Mumbai OU can take the quiz.']
        return redirect(url_for('home'))

    if has_attempted_quiz(current_user.username):
        session['flash_messages'] = ['You have already attempted the quiz.']
        return redirect(url_for('home'))

    if request.method == 'POST':
        for question_id in request.form:
            selected_option = request.form[question_id]
            response = Response(
                user=current_user.username,
                question_id=int(question_id[1:]),
                selected_option=int(selected_option)
            )
            db.session.add(response)
        db.session.commit()
        session['flash_messages'] = ['Quiz submitted successfully!']
        return redirect(url_for('home'))

    quiz_questions = Quiz.query.all()
    return render_template('take_quiz.html', questions=quiz_questions)

@app.route('/view_responses')
@login_required
def view_responses():
    if current_user.username.lower() != 'admin':
        session['flash_messages'] = ['Only admin can view responses.']
        return redirect(url_for('home'))

    responses = Response.query.all()
    user_scores = {response.user: calculate_user_score(response.user) for response in responses}
    return render_template('view_responses.html', responses=responses, user_scores=user_scores)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
