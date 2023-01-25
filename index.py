from flask import Flask, request, render_template, make_response, redirect, session, url_for, flash, send_file
from Block import *
from flask_qrcode import QRcode
from Field import Zn
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
QRcode(app)


# If the file exists import the Blockchain, otherwise create a new one


if os.path.exists("blockchain.txt"):
    blockchain = BlockChain.load_from_file("blockchain.txt")
else:
    p = 20333
    a = Zn(0, p)
    b = Zn(7, p)
    # Create the curve object
    curve = EllipticCurve(a, b)
    curve.set_generator(CurvePoint(Zn(15377, p), Zn(20134, p), curve))
    curve.set_order(3389)
    blockchain = BlockChain(curve)

@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == "POST":
        # Retrieve the user's input
        username = request.form['username']
        if username == "" or len(username) > 20:
            flash("Username can't be empty or longer than 20 characters")
            return redirect(url_for('signup'))
        if blockchain.get_user_by_name(username) is not None:
            flash("Username already exists")
            return redirect(url_for('signup'))
        session['latest_transaction'] = None
        while True:
            # Generate a private key for the user, 1 and 2 are reserved for Blockchain rewards
            private_key = random.randint(3, blockchain.curve.get_order() - 1)
            pubkey = blockchain.curve.get_generator() * private_key
            if blockchain.get_user(pubkey) is None:
                break

        # Create the user
        user = User(username, pubkey)
        blockchain.add_user(user)

        session["pubkey"] = str(user.pubkey)
        session["username"] = username
        session["privkey"] = private_key
        session["latest_received_transaction"] = None

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
            public_key = blockchain.curve.get_generator() * private_key
        except:
            flash("Invalid private key")
            return redirect(url_for('login'))
        if private_key == 1 or private_key == 2:
            flash("Invalid private key")
            return redirect(url_for('login'))
        if username == "God" or username == "bonus":
            flash("What are you trying to achieve you filthy cheater?")
            return redirect(url_for("login"))
        current_user = blockchain.get_user_by_name(username)
        if current_user is not None:
            if current_user.pubkey == public_key:
                session["username"] = username
                session["pubkey"] = str(public_key)
                session["privkey"] = private_key
                session["latest_transaction"] = None
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong private key")
                return redirect(url_for('login'))
        else:
            flash("Invalid username")
            return redirect(url_for('login'))
    else:
        return render_template("login.html")


@app.route('/logout', methods=['POST','GET'])
def logout():
    session.pop("username", None)
    session.pop("privkey", None)
    session.pop("pubkey", None)
    session.pop("balance", None)
    session.pop("latest_transaction", None)
    session["x"] = ""
    session["y"] = ""
    session.pop('_flashes', None)
    return render_template("logout.html")

@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    if "username" in session:
        username = session["username"]
        session["balance"] = blockchain.get_user_by_name(username).balance
        session["staking_power"] = blockchain.get_user_by_name(username).staking_power
        if request.method == "POST":
            if "send" in request.form:
                return redirect(url_for('send'))
            elif "transactions" in request.form:
                return redirect(url_for('transactions'))
            elif "blockchain" in request.form:
                return redirect(url_for('blockchain'))
            elif "logout" in request.form:
                return redirect(url_for('logout'))
        else:
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
            x = int(request.form['x'])
            y = int(request.form['y'])
            p = blockchain.curve.get_a().p
            try:
                amount = float(amount)
            except:
                flash("Invalid amount")
                return redirect(url_for('send'))
            try:
                recipient = CurvePoint(Zn(x, p), Zn(y, p), blockchain.curve)
            except:
                session["x"] = ""
                session["y"] = ""
                flash("Invalid Recipient")
                return redirect(url_for('send'))
            if blockchain.get_user_by_name(username).balance < amount:
                flash("Insufficient funds")
            elif amount <= 0:
                flash("Invalid amount")
            elif blockchain.get_user(recipient) is None:
                flash("Invalid recipient")
            elif blockchain.get_user(recipient).name == username:
                flash("Can't send to yourself")
            else:
                transaction = blockchain.make_transaction(blockchain.get_user_by_name(username).pubkey,
                                        session["privkey"], recipient, amount)
                fast = request.form.get('fast_transaction')
                if fast == "true":
                    blockchain.make_transaction(blockchain.get_user_by_name(username).pubkey, session["privkey"], blockchain.get_user_by_name("bonus").pubkey, 0.05*amount)
                    blockchain.mine()
                flash("Transaction sent")
                session["latest_transaction"] = str(transaction)
                session["x"] = ""
                session["y"] = ""
                return redirect(url_for('send'))

            return redirect(url_for('send'))
        else:
            return render_template("send.html",
                                   balance=blockchain.get_user_by_name(session["username"]).balance,
                                   username=session["username"])
    else:
        return redirect(url_for('homepage'))



@app.route('/qr_scan', methods=['POST','GET'])
def qr_scan():
    return render_template("qr_scan.html")

@app.route('/qr_code', methods=['POST', 'GET'])
def qr_code():
    qr_code_data = request.form["qr_code_scan"]
    x, y = read_string_coordinates(qr_code_data)
    session["x"] = x
    session["y"] = y

    return redirect(url_for('send'))

def read_string_coordinates(string):
    x, y = string.split(";")
    x = int(x[3:])
    y = int(y[3:])
    return x, y

@app.route('/latest_transactions', methods=['POST','GET'])
def latest_transactions():
    if "username" in session:
        if request.method == "POST":
            if "dashboard" in request.form:
                return redirect(url_for('dashboard'))
            elif "logout" in request.form:
                return redirect(url_for('logout'))
        num_transaction = request.args.get('num_transaction') or 5
        try:
            num_transaction = int(num_transaction)
        except:
            flash("Invalid number of transactions")
            return redirect(url_for('latest_transactions'))
        transactions_signed = blockchain.get_last_x_transaction(blockchain.get_user_by_name(session["username"]),num_transaction)
        transactions = []
        for transaction in transactions_signed:
            transaction = transaction[0]
            transactions.append({'sender': transaction.sender.name, 'amount': transaction.amount, 'receiver': transaction.receiver.name})
        return render_template("latest_transactions.html", balance=blockchain.get_user_by_name(session["username"]).balance,
                               username=session["username"], transactions=transactions)
    else:
        return redirect(url_for('homepage'))


@app.route('/download-blockchain')
def download_blockchain():
    blockchain_string = blockchain.chain_to_string()
    response = make_response(blockchain_string)
    response.headers["Content-Disposition"] = "attachment; filename=blockchain.txt"
    return response



@app.route('/staking', methods=['POST','GET'])
def staking():
    if "username" in session:
        user = blockchain.get_user_by_name(session["username"])
        staking_period = blockchain.stake.users[user][1] + blockchain.stake.unstaking_period - datetime.now()
        if request.method == "POST":
            if "stake" in request.form:
                amount = float(request.form["stake_amount"])
                if amount > user.balance:
                    flash("Insufficient funds")
                elif amount <= 0:
                    flash("Invalid amount")
                else:
                    blockchain.stake.stake_coins(user, amount)
                    flash("Coins staked")
            elif "unstake" in request.form:
                amount = float(request.form["stake_amount"])
                if amount > blockchain.stake.users[user][0]:
                    flash("Insufficient funds")
                elif amount <= 0:
                    flash("Invalid amount")
                elif blockchain.stake.unstake_coins(user, amount):
                    flash("Coins unstaked")
                else:
                    flash("Unstaking Period not over")
            blockchain.save_to_file("blockchain.txt")
        return render_template("staking.html", username=session["username"], balance=blockchain.get_user_by_name(session["username"]).balance,
                               staking_period=staking_period.total_seconds(), staked_amount=blockchain.stake.users[user][0],
                               staking_rate=user.staking_power)
    else:
        return redirect(url_for('homepage'))


@app.route('/notification', methods=['GET'])
def check_transaction_status():
    for trans in blockchain.get_last_x_transaction_sender(blockchain.get_user_by_name(session["username"]), 2):
        trans = trans[0]
        if str(trans) == session["latest_transaction"]:
            if trans.status == "Denied" or trans.status == "Complete":
                session["latest_transaction"] = None
                resp = {'status': trans.status, 'amount': trans.amount, 'receiver': trans.receiver.name}
                return make_response(resp)
    return make_response({'status': "Pending"})


@app.route('/receive', methods=['GET'])
def receive():
    for trans in blockchain.get_last_x_transaction_receiver(blockchain.get_user_by_name(session["username"]), 1):
        trans = trans[0]
        if str(trans) != session["latest_received_transaction"]:
            if trans.status == "Denied" or trans.status == "Complete":
                session["latest_received_transaction"] = str(trans)
                resp = {'status': trans.status, 'amount': trans.amount, 'sender': trans.sender.name}
                return make_response(resp)
    return make_response({'status': "Pending"})


@app.route('/information', methods=['POST','GET'])
def information():
    if request.method == "POST":
        if "dashboard" in request.form:
            return redirect(url_for('dashboard'))
        elif "logout" in request.form:
            return redirect(url_for('logout'))
        elif "homepage" in request.form:
            return redirect(url_for('homepage'))
    if "username" in session:
        return render_template("information.html", username=session["username"])
    else:
        return render_template("information.html", username="God")

if __name__ == '__main__':
    app.run(debug=True)