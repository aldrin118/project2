from flask import Flask, flash, redirect, render_template, request, session, abort,url_for
import os
import requests
import json

app = Flask(__name__)
app.secret_key = os.urandom(12)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register', methods=['GET','POST'])
def registerUser():
    if request.form['password'] == request.form['password2']:
        data = {"username":request.form['username'], "password":request.form['password']}
        url = 'https://database-api-latest.onrender.com/myapp/add_user/'
        response = requests.post(url, json=data)
        print(response.json())
        return home()
    else:
        msg = "Password missmatch"
        return render_template('register.html', msg=msg )
    
@app.route('/login')
def to_login():
    return render_template('login.html')

@app.route('/parking')
def to_parking():
    url = f'https://database-api-latest.onrender.com/myapp/get_available_locations/'
    response = requests.get(url)
    availableslot = []
    for item in response.json()['available_locations']:
        availableslot.append({'id':item['id'],'type': item['type']})
    return render_template('parking.html',links = availableslot)


@app.route('/parking', methods = ['POST'])
def getParkingSlots():
    slot = request.form['slots']
    url = f'https://database-api-latest.onrender.com/myapp/slot_type/?slot_id={slot}'
    response = requests.get(url)
    session['slot'] = slot
    session['type'] = response.json()
    return redirect(url_for('.reserve'))

@app.route('/makeReserve')
def reserve():
    slot = session['slot'] 
    type = session['type']
    return render_template("makeReserve.html", slot = slot, type=type)

@app.route('/makeReserve')
def to_makeReserve():
    return render_template('makeReserve.html')

@app.route('/makeReserve', methods=['POST'])
def reserveSlot():
    data = {'username': session['username'], 'slot_id': int(session['slot']) , 'expiry_hours': int(request.form['hours'])}
    url = f'https://database-api-latest.onrender.com/myapp/add_reservation/'
    response = requests.post(url, json=data)
    message = response.json()['message']
    return render_template('success.html',message = message)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/reserve')
def to_reserve():
    username = session['username']
    url = f'https://database-api-latest.onrender.com/myapp/get_your_reservations/?username={username}'
    response = requests.get(url)
    reservation = []
    print(reservation)
    for item in response.json()['reservations']:
        reservation.append(item)
    if len(reservation) < 1:
        reservation = "No Reservation"
    session['reservations'] = reservation

    return render_template('reserve.html' , reservation = reservation)

@app.route('/reserve', methods=['POST'])
def removeReserve():
    id = session['reservations'][0]['Slot_ID_id']
    url = f'https://database-api-latest.onrender.com/myapp/remove_reservation/'
    data = {"slot_id":id}
    respose = requests.delete(url,json=data)
    return render_template('success.html', message = respose.json()['message'])

@app.route('/feedback')
def to_feedback():
    return render_template('feedback.html')

@app.route('/feedback', methods=['POST'])
def postFeedback():
    return render_template('success.html', message = "Feedback submited")

@app.route('/main')
def to_main():    
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('main.html')
    
@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['username'] = ""
    return render_template('home.html')

    
@app.route('/login', methods=['POST'])
def do_admin_login():
    username = request.form['username']
    password = request.form['password']
    url = f'https://database-api-latest.onrender.com/myapp/authenticate_user/?username={username}&password={password}'
    response = requests.get(url)
    #authenticate_user(response)
    print(response.status_code)
    if response.status_code == 200:
        session['username'] = request.form['username']
        session['logged_in'] = True
    else:
        flash('Wrong password!')
    return to_main()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)
