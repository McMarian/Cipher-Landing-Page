document.querySelector(".account-button").addEventListener("click", function() {
    var dropdown = document.querySelector(".account-dropdown");
    dropdown.style.display = dropdown.style.display === "none" ? "block" : "none";
});

document.querySelector(".signup-form").addEventListener("submit", function(event) {
    event.preventDefault();

    var username = document.querySelector('#username-input').value;
    var password = document.querySelector('#password-input').value;

    fetch('http://localhost:3000/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password,
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        console.log(data);
        localStorage.setItem('username', username);
        window.location.href = 'profile.html'; 
    })
    .catch((error) => {
      console.error('Error:', error);
    });
});

document.querySelector(".login-form").addEventListener("submit", function(event) {
    event.preventDefault();

    var username = document.querySelector('#username-input').value;
    var password = document.querySelector('#password-input').value;

    fetch('http://localhost:3000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password,
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        console.log(data);
        
        localStorage.setItem('username', username);
        window.location.href = 'profile.html'; 
    })
    .catch((error) => {
      console.error('Error:', error);
    });
});