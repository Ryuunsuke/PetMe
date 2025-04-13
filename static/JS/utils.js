window.onclick = function(event) {
    if (event.target.classList.contains('loginmodal')) {
        document.getElementById('id01').style.display = "none";
    }
    if (event.target.classList.contains('registermodal')) {
        document.getElementById('id02').style.display = "none";
    }
    if (event.target.classList.contains('chat-container')) {
        document.getElementById('chatbox').style.display = "none";
    }
}

function closemodals(){
    document.getElementById('id01').style.display='none';
    document.getElementById('id02').style.display='none';
    document.getElementById('chatbox').style.display='none';
}

function showRegister() {
    document.getElementById('id01').style.display = 'none'; // Hide login modal
    document.getElementById('id02').style.display = 'block'; // Show register modal
}

function showLogin() {
    document.getElementById('id02').style.display = 'none'; // Hide register modal
    document.getElementById('id01').style.display = 'block'; // Show login modal
}

function openChat() {
    // Create a JSON object with the form data
    let email = $('#LEmail').val();
    let password = $('#LPSW').val();

    // Create a JSON object with the form data
    let data = {
        email: email,
        password: password
    };

    // Make the AJAX request
    $.ajax({
        type: 'POST',
        url: '/login',
        contentType: 'application/json', // Explicitly set the content type as JSON
        data: JSON.stringify(data),  // Convert the data object to a JSON string
        success: function(response){
            // Handle success response
            if (response.success) {
                const isLoggedIn = response.loggedin;
                if (isLoggedIn) {
                    document.getElementById('id01').style.display = 'none';
                    document.getElementById('id02').style.display = 'none';
                    document.getElementById('chatbox').style.display='flex';
                } else {
                    alert("You need to log in to use this feature.");
                    document.getElementById('id01').style.display='block';
                    document.getElementById('id02').style.display = 'none';
                    document.getElementById('chatbox').style.display='none';
                }
            } else {
                alert(response.message);  // Show error message
            }
        },
        error: function(){
            alert('Login failed. Please try again.');  // Handle unexpected errors
        }
    });
}

function logout() {
    document.getElementById('logmodal').reset();
    let email = $('#LEmail').val();
    let password = $('#LPSW').val();

    // Create a JSON object with the form data
    let data = {
        email: email,
        password: password
    };

    // Make the AJAX request
    $.ajax({
        type: 'POST',
        url: '/login',
        contentType: 'application/json', // Explicitly set the content type as JSON
        data: JSON.stringify(data),  // Convert the data object to a JSON string
        success: function(response){
            // Handle success response
            if (response.success) {
                openChat();
            } else {
                alert(response.message);  // Show error message
            }
        },
        error: function(){
            alert('Login failed. Please try again.');  // Handle unexpected errors
        }
    });
}