document.querySelector(".account-button").addEventListener("click", function() {
    var dropdown = document.querySelector(".account-dropdown");
    dropdown.style.display = dropdown.style.display === "none" ? "block" : "none";
});

document.querySelector(".signup-form").addEventListener("submit", function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    if (username && password) {
        register(username, password);
    } else {
        alert('Please fill in all fields.');
    }
});

document.querySelector(".login-form").addEventListener("submit", function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    if (username && password) {
        login(username, password);
    } else {
        alert('Please fill in all fields.');
    }
});

document.getElementById('new-post-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const content = document.getElementById('new-post-content').value;
    createPost(content);
    event.target.reset();  
});

document.getElementById('new-comment-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const postId = document.getElementById('post-id').value;
    const content = document.getElementById('new-comment-content').value;
    createComment(postId, content);
    event.target.reset();  
});

function register(username, password) {
    if (!username || !password) {
        alert('Username and password cannot be empty.');
        return;
    }

    if (password.length < 8 || !/\d/.test(password) || !/[a-zA-Z]/.test(password)) {
        alert('Password must be at least 8 characters long and contain at least one letter and one number.');
        return;
    }

    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'username': username,
            'password': password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'User created successfully') {
            window.location.href = data.redirect;
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while registering. Please try again.');
    });
}

function login(username, password) {
    if (!username || !password) {
        alert('Username and password cannot be empty.');
        return;
    }
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'username': username,
            'password': password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Logged in successfully') {
            window.location.href = data.redirect;
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while logging in. Please try again.');
    });
}

function fetchPosts() {
    fetch('/posts')
        .then(response => response.json())
        .then(posts => {
            const postsContainer = document.getElementById('posts-container');
            postsContainer.innerHTML = '';  

            posts.forEach(post => {
                const postElement = document.createElement('div');
                postElement.className = 'post';

                const titleElement = document.createElement('h2');
                titleElement.textContent = post.title;
                postElement.appendChild(titleElement);

                const contentElement = document.createElement('p');
                contentElement.textContent = post.content;
                postElement.appendChild(contentElement);

                const usernameElement = document.createElement('p');
                usernameElement.textContent = `Posted by: ${post.username}`;
                postElement.appendChild(usernameElement);

                const commentCountElement = document.createElement('p');
                commentCountElement.textContent = `${post.comments.length} comments`;
                postElement.appendChild(commentCountElement);

                postsContainer.appendChild(postElement);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching posts. Please try again.');
        });
}

function createPost(content) {
    fetch('/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'content': content
        })
    })
    .then(response => response.json())
    .then(post => {
        fetchPosts();  
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while creating the post. Please try again.');
    });
}

function updatePost(postId, content) {
    fetch(`/posts/${postId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'content': content
        })
    })
    .then(response => response.json())
    .then(post => {
        fetchPosts();  
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the post. Please try again.');
    });
}


function deletePost(postId) {
    fetch(`/posts/${postId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            fetchPosts();  
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while deleting the post. Please try again.');
    });
}

function createComment(postId, content) {
    fetch(`/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'content': content
        })
    })
    .then(response => response.json())
    .then(comment => {
        fetchPosts();  
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while creating the comment. Please try again.');
    });
}

function fetchComments(postId) {
    fetch(`/posts/${postId}/comments`)
        .then(response => response.json())
        .then(comments => {
            const commentsContainer = document.getElementById(`comments-${postId}`);
            commentsContainer.innerHTML = '';  
            comments.forEach(comment => {
                const commentElement = document.createElement('div');
                commentElement.textContent = `${comment.username}: ${comment.content}`;
                const timestampElement = document.createElement('p');
                timestampElement.textContent = `Posted on: ${new Date(comment.timestamp).toLocaleString()}`;
                commentElement.appendChild(timestampElement);
                commentsContainer.appendChild(commentElement);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching comments. Please try again.');
        });
}