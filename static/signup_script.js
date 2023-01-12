const signupForm = document.querySelector('#signup-form');

signupForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const formData = new FormData(signupForm);
  const username = formData.get('username');

  fetch('/signup', {
    method: 'POST',
    body: JSON.stringify({ username }),
    headers: { 'Content-Type': 'application/json' }
  })
    .then((response) => response.json())
    .then((data) => {
      // Handle the response data from the server,
      // such as displaying the private key on the page
    });
});
