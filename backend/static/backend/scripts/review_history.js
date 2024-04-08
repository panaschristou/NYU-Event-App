const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');


const clearHistoryButton = document.getElementById("clearHistoryButton");

  
document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('myModal2'); 
  const confirmDeleteButton = document.getElementById('confirmDeleteButton1');
  const cancelDeleteButton = document.getElementById('cancelDeleteButton1');
  const closeButton = document.getElementById("close-m1");



  reviews.forEach(review => {
    addReviewToPage(review);
  });

  clearHistoryButton.addEventListener("click", function() { 
    modal.style.display = 'block';
    closeButton.addEventListener("click", function () {
      modal.style.display = "none";
    });
  
    cancelDeleteButton.addEventListener('click', function() {
      modal.style.display = 'none';
    });
    confirmDeleteButton.addEventListener('click', function() {
      reviews.forEach(review => {
        deletereview(review.id);
      });
      modal.style.display = 'none';
    });
  });

});

function showTemporaryMessage(message, messageType) {
  const tempMessageContainer = document.createElement("div");
  tempMessageContainer.textContent = message;
  tempMessageContainer.classList.add("alert", messageType, "temp-message");
  
  document.body.appendChild(tempMessageContainer);

  setTimeout(() => {
    tempMessageContainer.remove();
  }, 2500);
}

function addReviewToPage(review) {
  const reviewBox = document.createElement('div');
  reviewBox.className = 'review-box';
  const avatarWrapper = document.createElement('div');
  avatarWrapper.className = 'avatar-wrapper';
  
  const event = document.createElement('h5');
  event.className = 'review-event';
  event.textContent = review.event.title;
  reviewBox.appendChild(event);

  reviewBox.appendChild(avatarWrapper);

  const content = document.createElement('div');
  content.className = 'review-content';


  const rating = document.createElement('p');
  rating.textContent = `Rating: ${review.rating}`;
  content.appendChild(rating);

  const text = document.createElement('p');
  if (review.review_text) {
    text.textContent = review.review_text;
  } else {
    text.textContent = 'you did not leave any review text';
    text.classList.add('lighter-text'); 
  }
  content.appendChild(text);

  reviewBox.appendChild(content);
  
  const timestamp = document.createElement('div');
  timestamp.className = 'review-date';
  timestamp.textContent = new Date(review.timestamp).toLocaleDateString();
  reviewBox.appendChild(timestamp);

  const buttonContainer = document.createElement('div');
  buttonContainer.className = 'review-button-container';
  buttonContainer.style.display = 'flex';
  buttonContainer.style.justifyContent = 'flex-end'; // Aligns buttons to the right
  buttonContainer.style.marginTop = '10px';

  const deleteButton = document.createElement('button');
  deleteButton.className = 'delete-button';
  deleteButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
    </svg>`;
  const modal = document.getElementById('myModal');
  const confirmDeleteButton = document.getElementById('confirmDeleteButton');
  const cancelDeleteButton = document.getElementById('cancelDeleteButton');
  const closeButton = document.getElementById("close-m");
  let index;

  deleteButton.addEventListener('click', function() {
    index=review.id;
    modal.style.display = 'block';
  });

  closeButton.addEventListener("click", function () {
    index=null;
    modal.style.display = "none";
  });

  cancelDeleteButton.addEventListener('click', function() {
    index=null;
    modal.style.display = 'none';
  });
  confirmDeleteButton.addEventListener('click', function() {
    deletereview(index);
    modal.style.display = 'none';
  });

  buttonContainer.appendChild(deleteButton);

  reviewBox.appendChild(buttonContainer);
  const reviewsContainer = document.getElementById('reviews-container');
  reviewsContainer.prepend(reviewBox);
}

function deletereview(reviewId) {
  let url = `${reviewId}/delete/`;
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json', 
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': csrftoken,
    },
    credentials: 'same-origin',
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    showTemporaryMessage("You have successfully deleted review.", "alert-success");
    setTimeout(function() {
    }, 2000);
  })
  .catch(error => {
    console.error('Error:', error);
  });
}






