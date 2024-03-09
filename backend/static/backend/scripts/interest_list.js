const notInterestBtns = document.getElementsByClassName("remove-interest");
Array.from(notInterestBtns).forEach((btn) => {
  btn.addEventListener("click", (e) => {
    const event_id = e.currentTarget.getAttribute("event-id");
    fetch(`/user/events/${event_id}/remove-interest/`, {
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
        location.reload(true);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
});
