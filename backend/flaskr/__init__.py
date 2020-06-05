import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, literal
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  cors = CORS(app, resources={r"/api/": {"origins": "*"}})

  @app.after_request
  def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Headers", "GET, POST, PATCH, DELETE,OPTIONS")
        return response

  '''
  
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route("/")
  def home():
      return jsonify({
          "success":True,
      })

# TODO: i still have problem with pagination

  @app.route('/questions/', methods=['GET'])
  def questions():
    page = request.args.get("page", 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE

    questions_objects = Question.query.all()
    questions_list = [qstion.format() for qstion in questions_objects]

    categories = Category.query.all()
    categories_dict = {cat.id: cat.type for cat in categories}

    return jsonify({
        "success": True,
        "questions": questions_list,
        "totalQuestions": len(questions_list),
        "categories": categories_dict,
        "currentCategory": None
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
  # Done

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
     

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  # @app.route("/play")
  # def play():
  #   return "rerer"
        

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  Done :)
  '''
  # @app.errorhandler(404)
  # def not_found(error):
  #   return jsonify({
  #     "success":False,
  #     "error":404,
  #     "message":"Not Found"
  #     }),404
  
  # @app.errorhandler(422)
  # def not_found(error):
  #   return jsonify({
  #       "success": False,
  #       "error": 422,
  #       "message": "Not Found"
  #   }), 422


  return app

    
