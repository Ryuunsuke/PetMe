document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('regmodal').reset();
    document.getElementById('regmodal').addEventListener('submit', async function (e) {
        e.preventDefault();  // Prevent the form from submitting the normal way

        const email = document.getElementById('REmail').value;
        const password = document.getElementById('RPSW').value;

        const data = JSON.stringify({ email, password });

        console.log("Sending data:", data);  // Debugging

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: data
            });

            const result = await response.json();

            if (result.success) {
                alert('Client registered successfully!');
                showLogin()
                document.getElementById('regmodal').reset();
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
});

