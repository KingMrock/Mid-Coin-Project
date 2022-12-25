from flask import Flask, request, render_template, make_response
from Block import *

app = Flask(__name__, template_folder='templates', static_folder='static')
b_chain = BlockChain()
b_chain.add_miner(Miner("Alice"))




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transactions', methods=['POST'])
def new_transaction():
    # get the transaction data from the request
    transaction_data = request.get_json()
    transaction_str = handle_transaction(transaction_data)
    add_transaction_to_history(transaction_str)

    # add the transaction to the list of pending transactions
    b_chain.add_transaction(transaction_str)
    print(b_chain.pending_transactions)
    return 'Transaction added successfully.'

@app.route('/chain', methods=['GET'])
def get_chain():
    # return the full blockchain
    return b_chain.print_chain()

@app.route('/get-blockchain')
def get_blockchain():
    blockchain_str = b_chain.print_chain()
    response = make_response(blockchain_str)
    response.headers["Content-Disposition"] = "attachment; filename=blockchain.txt"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)