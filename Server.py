from flask import Flask, request, render_template, make_response, jsonify, redirect, session, url_for, flash
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

        # Generate a private key for the user
        private_key = random.randint(1, blockchain.curve.get_order() - 1)

        # Create the user
        user = User(username, private_key, blockchain.curve.get_generator() * private_key)
        blockchain.add_user(user)

        session["pubkey"] = str(user.pubkey)
        session["username"] = username
        session["privkey"] = private_key

        return redirect(url_for('privatekey'))
    else:
        return render_template("signup.html")

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
        temp = request.form['privkey']
        try:
            private_key = int(temp)
        except:
            flash("Invalid private key")
            return redirect(url_for('login'))
        pubkey = private_key * blockchain.curve.get_generator()
        if blockchain.get_user_by_name(username) is not None and blockchain.get_user_by_name(username).pubkey == pubkey:
            session["username"] = username
            session["pubkey"] = str(pubkey)
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

@app.route('/dashboard')
def dashboard():
    if "username" in session:
        username = session["username"]
        session["balance"] = blockchain.get_user_by_name(username).balance
        session["staking_power"] = blockchain.get_user_by_name(username).staking_power
        return render_template("dashboard.html", username=username, pubkey=session["pubkey"], balance=session["balance"], staking_power=session["staking_power"])
    else:
        return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run(debug=True)
