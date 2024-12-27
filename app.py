from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

RESPONSE_KEY = 'response'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route('/')
def enable_survey_start():
    """Form is shown for the user to pick a survey to complete"""

    return render_template('start_survey.html')

@app.route('/start', methods=["POST"])
def start_survey():
    """Clear the session and of survey responses"""

    session[RESPONSE_KEY] = []

    return redirect('/question/0')

@app.route('/answer', methods=["POST"])
def handle_question():
    """Save the users response and move to next question"""

    choice = request.form['answer']

    responses = session[RESPONSE_KEY]
    responses.append(choice)
    session[RESPONSE_KEY] = responses

    if (len(responses) == len(survey.questions)):
        return redirect('/complete')
    
    else: 
        return redirect(f"/questions/{len(responses)}")
    

@app.route('/questions/<int:qid>')
def show_quesition(qid):
    """Shows the current questions for user to answer"""

    responses = session.get(RESPONSE_KEY)

    if (responses is None):
        return redirect('/')

    if (len(responses) == len(survey.questions)):
        return redirect('/complete')
    
    if (len(responses) != qid):
        flash(f"Invalid Question ID: {qid}")
        return redirect(f"/questions/{len(responses)}")
    
    question = survey.question[qid]

    return render_template('question.html', question_num=qid, question=question)


@app.route('/complete')
def survey_completed():
    """Shows survey completed page and thanks the user"""

    return render_template('completed.html')