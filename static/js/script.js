document.addEventListener('DOMContentLoaded', function() {
  const registerButton = document.getElementById('register-button');
  const loginButton = document.getElementById('login-button');

  registerButton.addEventListener('click', function() {
      const username = document.getElementById('register-username').value;
      const password = document.getElementById('register-password').value;

      fetch('/register', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              username: username,
              password: password
          })
      })
      .then(response => response.json())
      .then(data => {
          alert(data.message);
      })
      .catch(error => {
          console.error('Error:', error);
      });
  });

  loginButton.addEventListener('click', function() {
      const username = document.getElementById('login-username').value;
      const password = document.getElementById('login-password').value;

      fetch('/login', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              username: username,
              password: password
          })
      })
      .then(response => response.json())
      .then(data => {
          if (data.token) {
              window.location.href = '/protected-page?token=' + data.token;
          } else {
              alert(data.message);
          }
      })
      .catch(error => {
          console.error('Error:', error);
      });
  });
});
