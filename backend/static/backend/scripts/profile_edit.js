const csrftoken = $('meta[name="csrf-token"]').attr("content");

$(".delete_account")[0].addEventListener("click", () => {
  fetch("/user/delete-account", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
  })
    .then((response) => {
      window.location.replace("/user/login");
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});

const avatarInput = document.getElementById("avatar-input");
const imageBox = document.getElementById("image-box");
avatarInput.addEventListener("change", () => {
  console.log("change");
  const imgFile = avatarInput.files[0];
  const imgUrl = URL.createObjectURL(imgFile);
  imageBox.innerHTML = `<img id="image-cropper" class="hidden" width="400px" src=${imgUrl} />`;

  const image = document.getElementById("image-cropper");
  const cropper = new Cropper(image, {
    aspectRatio: 1 / 1,
    crop(event) {
      console.log(event.detail.x);
      console.log(event.detail.y);
      console.log(event.detail.width);
      console.log(event.detail.height);
      console.log(event.detail.rotate);
      console.log(event.detail.scaleX);
      console.log(event.detail.scaleY);
    },
  });
});
