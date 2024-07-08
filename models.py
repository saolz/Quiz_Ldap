from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class Response(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user = db.Column(db.String(50), nullable=False)
        question_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
        selected_option = db.Column(db.Integer, nullable=False)
        quiz = db.relationship('Quiz', backref=db.backref('responses', lazy=True))