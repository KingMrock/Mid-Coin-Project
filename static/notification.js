setInterval(function() {
    fetch('/notification')
    .then(function(response) {
    return response.json();
    })
    .then(function(data) {
        if (data['status'] == "Complete") {
            console.log("Transaction Complete");
            toastr.success("Transaction of " + data.amount + " ᙢ to " + data.receiver + " is complete");
        }
        else if (data['status'] == "Denied") {
            toastr.error("Transaction of " + data.amount + " to " + data.receiver + " is denied");
        }
        else if (data['status'] == "Pending")
        {
            null;
        }
        else{
            null;
        }
    });
    fetch('/receive')
    .then(function(response) {
    return response.json();
    })
    .then(function(data) {
        if (data['status'] == "Complete") {
            toastr.info("You have received " + data.amount + " ᙢ from " + data.sender);
        }
        else if (data['status'] == "Pending")
        {
            null;
        }
        else{
            null;
        }
    });
}, 4000)