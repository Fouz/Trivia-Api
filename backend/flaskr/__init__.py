import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, literal
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
  page = request.args.get('page',1,type=int)
  start = (page-1)*QUESTIONS_PER_PAGE
  end = start+QUESTIONS_PER_PAGE

  formated_questions = [question.format() for question in selection]
  current_questions = formated_questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

  @app.route("/")
  def home():
      return jsonify({
          "success":True,
      })

  @app.route('/questions', methods=['GET'])
  def questions():
    page = request.args.get('page', 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE

    questions_objects = Question.query.all()
    questions = paginate_questions(request, questions_objects)

    categories = Category.query.all()
    categories_dict = {cat.id: cat.type for cat in categories}
    if len(questions) == 0:
      abort(404)
      return jsonify({
        'success':False
      })

    return jsonify({
        "success": True,
        "questions": paginate_questions(request,questions_objects),
        "total_questions": len(questions_objects),
        "categories": categories_dict,
        "current_category": {}
    })

  @app.route("/categories/<int:id>/questions",methods=["GET"])
  def current_category_questions(id):
        
    current = db.session.query(Category).get(id)
    current_questions = db.session.query(Question).join(
        Category, current.id == Question.category).all()

    questions_list = [qstion.format() for qstion in current_questions]
    
    return jsonify({
        "success": True,
        "questions": questions_list,
        "totalQuestions": len(questions_list),
        "currentCategory":current.format()
    })

  @app.route("/questions" ,methods=["POST"])
  def search():
    form = request.get_json()
    search_term = form.get('searchTerm')
    questions = db.session.query(Question).filter(func.lower(
        Question.question).contains(func.lower(literal(search_term)))).all()
    questions_list = [question.format() for question in questions]

    return jsonify({
      "success":True,
      "questions": questions_list,
      "totalQuestions": len(questions_list),
      "currentCategory": {}
    })

  @app.route("/questions/<int:id>", methods=['DELETE'])
  def delte_question(id):
    question = db.session.query(Question).get(id)
    try:
      question.delete()
    except:
      db.session.rollback()
    finally:
      db.session.close()
    
    return jsonify({
      "success":True
    })

  @app.route("/categories", methods=["GET"])
  def categories():
    categories_list = [cat.format() for cat in Category.query.all()]

    return jsonify({
      "success":True,
      "categories": {category["id"]: category["type"]
                      for category in categories_list},
    })
  @app.route("/add")
  def add_question():
        return jsonify({
          "success":True
        })
  @app.route("/questions/add", methods=["POST"])
  def add_questions():
    form = request.get_json ()
    ques = form.get('question')
    answer = form.get('answer')
    difficulty = form.get('difficulty')
    category = form.get('category')

    try:
      question = Question(question=ques, answer=answer, category=category, difficulty=difficulty)
      question.insert()
    except:
      db.session.rollback()
    finally:
      db.session.close()
    return jsonify({
        "success": True,
      })


  @app.route("/play")
  def play():
        return jsonify({
            "success": True
        })
  @app.route("/quizzes", methods=["POST"])
  def quizzes():
    form = request.get_json()
    previous_questions = form.get('previous_questions')
    quiz_category = form.get('quiz_category')
    try:
      questions = Question.query.filter_by(category=quiz_category['id']).filter(
          Question.id.notin_(previous_questions)).all()
      if len(questions) > 0:
        question = random.choice(questions).format()
        result = {
            "success": True,
            "question": question
        }
      else:
        result = {
            "success": True,
            "question": None
        }
      return jsonify(result)
    except:
      abort(422)

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success":False,
      "error":404,
      "message":"Not Found"
      }),404
  
  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Not Found"
    }), 422


  return app

    
