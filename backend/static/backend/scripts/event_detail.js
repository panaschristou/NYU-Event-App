const interestBtn = document.getElementById("add-interest");
const notInterestBtn = document.getElementById("remove-interest");

interestBtn.addEventListener("click", function () {
  fetch("add-interest/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // Include CSRF token from meta tag
      //   "X-CSRFToken": document
      //     .querySelector('meta[name="csrf-token"]')
      //     .getAttribute("content"),
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      notInterestBtn.classList.remove("hidden");
      interestBtn.classList.add("hidden");
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});

notInterestBtn.addEventListener("click", function () {
  fetch("remove-interest/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // Include CSRF token from meta tag
      //   "X-CSRFToken": document
      //     .querySelector('meta[name="csrf-token"]')
      //     .getAttribute("content"),
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      interestBtn.classList.remove("hidden");
      notInterestBtn.classList.add("hidden");
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});

//Rate and review functionality
const reviewBtn = document.getElementById("write-review");
const modal = document.getElementById("review-modal");
const closeButton = document.getElementById("close-modal");
const postButton = document.getElementById("post-review");
const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

reviewBtn.addEventListener("click", function () {
  resetReviewForm();
  modal.style.display = "block";
});

closeButton.addEventListener("click", function () {
  modal.style.display = "none";
});

postButton.addEventListener("click", function () {
  const selectedRating = document.querySelector('input[name="rating"]:checked');
  const reviewText = document.getElementById("review-text").value;
  const messagesContainer = document.getElementById("messages-container");

  messagesContainer.innerHTML = '';

  if (!selectedRating) {
    const errorMsg = document.createElement("div");
    errorMsg.textContent = "Please select a rating before posting your review.";
    errorMsg.classList.add("alert", "alert-danger"); 
    messagesContainer.appendChild(errorMsg);
    return; 
  }

  const rating = document.querySelector('input[name="rating"]:checked').value;

  const formData = new FormData();
  formData.append('rating', rating);
  formData.append('review_text', reviewText);

  fetch("post-review/", {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest', 
      'X-CSRFToken': csrftoken,
    },
    credentials: 'same-origin',
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok ' + response.statusText);
    }
    return response.json(); 
  })
  .then(data => {
    if (data.success) {
    showTemporaryMessage("Thank you for your review!", "alert-success");
    modal.style.display = "none";
    document.getElementById("review-text").value = '';
    document.querySelectorAll('input[name="rating"]').forEach((input) => {
      input.checked = false;
    });
    updateAverageRating(eventId);
    resetReviewForm();
    addReviewToPage(data.review);
  }else{
    showTemporaryMessage(data.message, "alert-danger");
  }
})
  .catch(error => {
    console.error('Error:', error);
    const errorMsg = document.createElement("div");
    errorMsg.textContent = "An error occurred while posting your review. Please try again.";
    errorMsg.classList.add("alert", "alert-danger"); 
    messagesContainer.appendChild(errorMsg);
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

function resetReviewForm() {
  document.getElementById("review-text").value = '';
  document.querySelectorAll('input[name="rating"]').forEach((input) => {
    input.checked = false;
  });
  // Clear any messages that might be inside the modal
  document.getElementById("messages-container").innerHTML = '';
}

function updateAverageRating(eventId) {
  fetch("avg-rating", {
    method: 'GET',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    },
    credentials: 'same-origin',
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    const avgRatingElement = document.getElementById("average-rating");
    if (data.avg_rating !== null && data.avg_rating !== undefined) {
      avgRatingElement.textContent = data.avg_rating.toFixed(2);
    } else {
      avgRatingElement.textContent = "Not rated yet";
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

document.addEventListener('DOMContentLoaded', function() {
  loadReviews(eventId);
  window.onscroll = function() {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
          loadReviews(eventId);
      }
  };
});

let currentPage = 1; 
let isLoading = false;
let hasMorePages = true;

function loadReviews(eventId) {
  if (isLoading || !hasMorePages) {
    return;
  }

  isLoading = true;

  fetch(`display-reviews`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrftoken,
      },
      credentials: 'same-origin',
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    } else if (!response.headers.get("content-type").includes("application/json")) {
      throw new Error("Not a JSON response");
    }
    return response.json();
  })
  .then(data => {
    
    data.reviews.forEach(review => {
      addReviewToPage(review);
    });
    

    if (!data.has_next) {
      hasMorePages = false; 
    }

    currentPage++;
    isLoading = false;
  })
  .catch(error => {
      console.error('Error fetching reviews:', error);
      isLoading = false;
  });
}


function addReviewToPage(review) {
  const reviewBox = document.createElement('div');
  reviewBox.className = 'review-box';
  const avatarWrapper = document.createElement('div');
  avatarWrapper.className = 'avatar-wrapper';

  const avatar = document.createElement('img');
  avatar.className = 'user-avatar';
  avatar.src = review.user.profile.avatar || '/backend/static/backend/img/generic_user_image.png';
  avatarWrapper.appendChild(avatar);

  reviewBox.appendChild(avatarWrapper);

  const content = document.createElement('div');
  content.className = 'review-content';

  const username = document.createElement('h5');
  username.className = 'review-username';
  username.textContent = review.user.username;
  reviewBox.appendChild(username);

  const rating = document.createElement('p');
  rating.textContent = `Rating: ${review.rating}`;
  content.appendChild(rating);

  const text = document.createElement('p');
  if (review.review_text) {
    text.textContent = review.review_text;
  } else {
    text.textContent = 'This user did not leave any review text';
    text.classList.add('lighter-text'); // Use this class to style placeholder text differently
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

  
  let likeCount = review.likes_count;
  const likeCountSpan = document.createElement('span');
  likeCountSpan.className = 'like-count';
  likeCountSpan.textContent = likeCount.toString();
  buttonContainer.appendChild(likeCountSpan);
  
  let  isLiked;
  if (review.liked_by.includes(currentUsername)) {
    isLiked=true;
} else {
  isLiked=false;
}
  const likeButton = document.createElement('button');
  likeButton.className = 'like-button';
  updateButtonAppearance(); 
  
  likeButton.addEventListener('click', function() {
      isLiked = !isLiked; 
      if (isLiked) {
          likeCount++;
      } else {
          likeCount--;
      }
      updateButtonAppearance(); 
      likeCountSpan.textContent = likeCount.toString(); 
      updateAllReviewsLikesCount(likeCount, review.id, isLiked);
  });
  
  buttonContainer.appendChild(likeButton);
  document.body.appendChild(buttonContainer);
  

  function updateAllReviewsLikesCount(likeCount, Id, isLiked) {
    fetch(`display-reviews/`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrftoken,
      },
      credentials: 'same-origin',
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      const reviews = data.reviews;
      const reviewIds = reviews.map(review => review.id);
      console.log(reviewIds);
      let url;
      if(isLiked){
        url = `display-reviews/${Id}/likes/`;
      }else{
        url = `display-reviews/${Id}/unlike/`;
      }
      fetch(url, {
        method: 'POST',
        body: JSON.stringify({ id: Id }), 
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

      })
      .catch(error => {
        console.error('Error:', error);
      
      });
    })
    .catch(error => {
      console.error('Error:', error);
     
    });
  }

  function updateButtonAppearance() { 
      if (isLiked) {
          likeButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-hand-thumbs-up-fill" viewBox="0 0 16 16">
              <path d="M6.956 1.745C7.021.81 7.908.087 8.864.325l.261.066c.463.116.874.456 1.012.965.22.816.533 2.511.062 4.51a10 10 0 0 1 .443-.051c.713-.065 1.669-.072 2.516.21.518.173.994.681 1.2 1.273.184.532.16 1.162-.234 1.733q.086.18.138.363c.077.27.113.567.113.856s-.036.586-.113.856c-.039.135-.09.273-.16.404.169.387.107.819-.003 1.148a3.2 3.2 0 0 1-.488.901c.054.152.076.312.076.465 0 .305-.089.625-.253.912C13.1 15.522 12.437 16 11.5 16H8c-.605 0-1.07-.081-1.466-.218a4.8 4.8 0 0 1-.97-.484l-.048-.03c-.504-.307-.999-.609-2.068-.722C2.682 14.464 2 13.846 2 13V9c0-.85.685-1.432 1.357-1.615.849-.232 1.574-.787 2.132-1.41.56-.627.914-1.28 1.039-1.639.199-.575.356-1.539.428-2.59z"/>
              </svg>`;
      } else {
          likeButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-hand-thumbs-up" viewBox="0 0 16 16">
              <path d="M8.864.046C7.908-.193 7.02.53 6.956 1.466c-.072 1.051-.23 2.016-.428 2.59-.125.36-.479 1.013-1.04 1.639-.557.623-1.282 1.178-2.131 1.41C2.685 7.288 2 7.87 2 8.72v4.001c0 .845.682 1.464 1.448 1.545 1.07.114 1.564.415 2.068.723l.048.03c.272.165.578.348.97.484.397.136.861.217 1.466.217h3.5c.937 0 1.599-.477 1.934-1.064a1.86 1.86 0 0 0 .254-.912c0-.152-.023-.312-.077-.464.201-.263.38-.578.488-.901.11-.33.172-.762.004-1.149.069-.13.12-.269.159-.403.077-.27.113-.568.113-.857 0-.288-.036-.585-.113-.856a2 2 0 0 0-.138-.362 1.9 1.9 0 0 0 .234-1.734c-.206-.592-.682-1.1-1.2-1.272-.847-.282-1.803-.276-2.516-.211a10 10 0 0 0-.443.05 9.4 9.4 0 0 0-.062-4.509A1.38 1.38 0 0 0 9.125.111zM11.5 14.721H8c-.51 0-.863-.069-1.14-.164-.281-.097-.506-.228-.776-.393l-.04-.024c-.555-.339-1.198-.731-2.49-.868-.333-.036-.554-.29-.554-.55V8.72c0-.254.226-.543.62-.65 1.095-.3 1.977-.996 2.614-1.708.635-.71 1.064-1.475 1.238-1.978.243-.7.407-1.768.482-2.85.025-.362.36-.594.667-.518l.262.066c.16.04.258.143.288.255a8.34 8.34 0 0 1-.145 4.725.5.5 0 0 0 .595.644l.003-.001.014-.003.058-.014a9 9 0 0 1 1.036-.157c.663-.06 1.457-.054 2.11.164.175.058.45.3.57.65.107.308.087.67-.266 1.022l-.353.353.353.354c.043.043.105.141.154.315.048.167.075.37.075.581 0 .212-.027.414-.075.582-.05.174-.111.272-.154.315l-.353.353.353.354c.047.047.109.177.005.488a2.2 2.2 0 0 1-.505.805l-.353.353.353.354c.006.005.041.05.041.17a.9.9 0 0 1-.121.416c-.165.288-.503.56-1.066.56z"/>
              </svg>`;
      }
  }
    
  const replyButton = document.createElement('button');
  replyButton.className = 'reply-button';
  replyButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chat-square-text" viewBox="0 0 16 16">
  <path d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1h-2.5a2 2 0 0 0-1.6.8L8 14.333 6.1 11.8a2 2 0 0 0-1.6-.8H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zM2 0a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2.5a1 1 0 0 1 .8.4l1.9 2.533a1 1 0 0 0 1.6 0l1.9-2.533a1 1 0 0 1 .8-.4H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>
  <path d="M3 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5M3 6a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 6m0 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5"/>
  </svg>`;

  // Event listener to switch to filled icon when hovered
  replyButton.addEventListener('mouseenter', function() {
    this.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chat-square-text-fill" viewBox="0 0 16 16">
    <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.5a1 1 0 0 0-.8.4l-1.9 2.533a1 1 0 0 1-1.6 0L5.3 12.4a1 1 0 0 0-.8-.4H2a2 2 0 0 1-2-2zm3.5 1a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1zm0 2.5a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1zm0 2.5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1z"/>
    </svg>`;
  });

  // Event listener to switch back to hollow icon when not hovered
  replyButton.addEventListener('mouseleave', function() {
    this.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chat-square-text" viewBox="0 0 16 16">
    <path d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1h-2.5a2 2 0 0 0-1.6.8L8 14.333 6.1 11.8a2 2 0 0 0-1.6-.8H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zM2 0a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2.5a1 1 0 0 1 .8.4l1.9 2.533a1 1 0 0 0 1.6 0l1.9-2.533a1 1 0 0 1 .8-.4H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>
    <path d="M3 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5M3 6a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 6m0 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5"/>
    </svg>`;
  });

  buttonContainer.appendChild(replyButton);

  if (currentUsername === review.user.username) {
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
     
      index = review.id;
      modal.style.display = 'block';
    });
  
    closeButton.addEventListener("click", function () {
      index = null;
      modal.style.display = "none";
    });
  
    cancelDeleteButton.addEventListener('click', function() {
      index = null;
      modal.style.display = 'none';
    });
  
    function deletereview(reviewId) {
      let url = `display-reviews/${reviewId}/delete/`;
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
       
        updateAverageRating(eventId);

        showTemporaryMessage("You have successfully deleted the review.", "alert-success");
        setTimeout(function() {
          setTimeout(function() {
            window.location.reload();
          }, 2000);
        }, 2000);
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }

    confirmDeleteButton.addEventListener('click', function() {
      deletereview(index);
      modal.style.display = 'none';
    });
  
    buttonContainer.appendChild(deleteButton);
  }

  reviewBox.appendChild(buttonContainer);

  const reviewsContainer = document.getElementById('reviews-container');
  reviewsContainer.prepend(reviewBox);
}