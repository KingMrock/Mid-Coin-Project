document.getElementById('transaction-form').addEventListener('submit', function(event) {
  event.preventDefault();
  // get the form values
  var from = document.getElementById('from').value;
  var to = document.getElementById('to').value;
  var amount = document.getElementById('amount').value;
  // create the transaction object
  var transaction = {
    'from': from,
    'to': to,
    'amount': amount
  };
  // make an HTTP POST request to the /transactions endpoint
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/transactions');
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onload = function() {
    if (xhr.status === 201) {
      console.log('Transaction added to the blockchain.');
    } else {
      console.error('Error adding transaction to the blockchain.');
    }
  };
  xhr.send(JSON.stringify(transaction));
});

function displayBlockchain() {
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      var blockchain = xhr.responseText;
      document.getElementById('blockchain-display').innerHTML = blockchain;
    }
  }
  xhr.open('GET', '/chain', true);
  xhr.send(null);
}

function downloadBlockchain() {
  var link = document.getElementById('download-link');
  link.href = '/get-blockchain';
  link.click();
}