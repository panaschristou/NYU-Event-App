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

  const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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
  }})
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
  fetch(`/event/${eventId}/avg_rating`, {
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
    if (data.avg_rating !== undefined) {
      avgRatingElement.textContent = data.avg_rating.toFixed(2);
    } else {
      avgRatingElement.textContent = "Not rated yet";
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}


