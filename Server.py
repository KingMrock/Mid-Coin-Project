from flask import Flask, request, render_template, make_response, jsonify, redirect, session, url_for, flash, \
    send_from_directory, send_file
from Block import *
import qrcode
from PIL import Image

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
blockchain = BlockChain.load_from_file("blockchain.txt")


def generate_qr_code(public_key):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(public_key)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("public_key_qr.jpg")


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == "POST":
        # Retrieve the user's input
        username = request.form['username']


        while True:
        # Generate a private key for the user
            private_key = random.randint(1, blockchain.curve.get_order() - 1)
            pubkey = blockchain.curve.get_generator() * private_key
            if blockchain.get_user(pubkey) is None:
                break


        # Create the user
        user = User(username, pubkey)
        blockchain.add_user(user)

        session["pubkey"] = str(user.pubkey)
        session["username"] = username
        session["privkey"] = private_key

        return redirect(url_for('privatekey'))
    else:
        return render_template("signup.html")


@app.route('/qr_code_generate', methods = ['GET'])
def qr_code_generate():
    pubkey = session["pubkey"]
    generate_qr_code(pubkey)
    return send_file("public_key_qr.jpg", mimetype='image/jpg')

@app.route('/privatekey')
def privatekey():
    if "username" in session:
        username = session["username"]
        privkey = session["privkey"]
        return render_template("privatekey.html", username=username, privkey=privkey)
    else:
        return redirect(url_for('/'))


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        temp = request.form['recipient']
        try:
            recipient = int(temp)
        except:
            flash("Invalid private key")
        if blockchain.get_user(recipient) is not None:
            session["username"] = username
            session.pop("privkey", None)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or private key")
            return redirect(url_for('login'))
    else:
        return render_template("login.html")


@app.route('/logout', methods=['POST','GET'])
def logout():
    session.pop("username", None)
    session.pop("privkey", None)
    session.pop("pubkey", None)
    session.pop("balance", None)
    flash("You have been logged out", "info")
    return redirect(url_for('homepage'))

@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    if "username" in session:
        username = session["username"]
        session["balance"] = blockchain.get_user_by_name(username).balance
        session["staking_power"] = blockchain.get_user_by_name(username).staking_power
        if request.method == "POST":
            if "send" in request.form:
                return redirect(url_for('send'))
            elif "receive" in request.form:
                return redirect(url_for('receive'))
            elif "transactions" in request.form:
                return redirect(url_for('transactions'))
            elif "blockchain" in request.form:
                return redirect(url_for('blockchain'))
            elif "logout" in request.form:
                return redirect(url_for('logout'))
        else:
            generate_qr_code(session["pubkey"])
            return render_template("dashboard.html", username=username, pubkey=session["pubkey"],
                                   balance=session["balance"], staking_power=session["staking_power"])
    else:
        return redirect(url_for('homepage'))


@app.route('/send', methods=['POST','GET'])
def send():
    if "username" in session:
        if request.method == "POST":
            username = session["username"]
            amount = request.form['amount']
            recipient = request.form['recipient']
            try:
                amount = int(amount)
            except:
                flash("Invalid amount")
                return redirect(url_for('send'))
            if blockchain.get_user_by_name(username).balance < amount:
                flash("Insufficient funds")
                return redirect(url_for('send'))
            if blockchain.get_user_by_name(recipient) is None:
                flash("Invalid recipient")
                return redirect(url_for('send'))
            if blockchain.get_user_by_name(username).balance < amount:
                flash("Insufficient funds")
                return redirect(url_for('send'))
            blockchain.send(username, recipient, amount)
            flash("Transaction successful")
            return redirect(url_for('dashboard'))
        else:
            return render_template("send.html")
    else:
        return redirect(url_for('homepage'))



@app.route('/qr_scan', methods=['POST','GET'])
def qr_scan():
    return render_template("qr_scan.html")

@app.route('/qr_code', methods=['POST'])
def qr_code():
    qr_code_data = request.form["qr_code_scan"]
    x, y = qr_code_data.split(";")
    x = int(x[3:])
    y = int(y[3:])
    session["x"] = x
    session["y"] = y

    return redirect(url_for('send'))

if __name__ == '__main__':
    app.run(debug=True)
