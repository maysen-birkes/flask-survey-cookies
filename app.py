from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

CURRENT_SURVEY_KEY = 'current-survey'
RESPONSE_KEY = 'response'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route('/')
def enable_pick_survey_form():
    """Form is shown for the user to pick a survey to complete"""

    return render_template('pick-survey.html', surveys=surveys)


@app.route('/', methods=["POST"])
def user_pick_survey():
    """User selects a survey to complete."""

    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template('already-done.html')
    
    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("start_survey.html", survey=survey)


@app.route('/start', methods=["POST"])
def start_survey():
    """Clear the session and of survey responses"""

    session[RESPONSE_KEY] = []

    return redirect('/questions/0')


@app.route('/answer', methods=["POST"])
def handle_question():
    """Save the users response and move to next question"""

    choice = request.form['answer']
    text = request.form.get('text', '')

    responses = session[RESPONSE_KEY]
    responses.append({"choice": choice, "text": text})

    session[RESPONSE_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        return redirect('/complete')
    
    else: 
        return redirect(f"/questions/{len(responses)}")
    

@app.route('/questions/<int:qid>')
def show_quesition(qid):
    """Shows the current questions for user to answer"""

    responses = session.get(RESPONSE_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if responses is None:
        return redirect('/')

    if len(responses) == len(survey.questions):
        return redirect('/complete')
    
    if len(responses) != qid:
        flash(f"Invalid Question ID: {qid}")
        return redirect(f"/questions/{len(responses)}")
    
    question = survey.questions[qid]

    return render_template('question.html', 
                           question_num=qid, 
                           question=question)


@app.route('/complete')
def survey_completed():
    """Shows survey completed page and thanks the user"""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSE_KEY]

    html = render_template('completed.html',
                           survey=survey,
                           responses=responses)
    
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)

    return response