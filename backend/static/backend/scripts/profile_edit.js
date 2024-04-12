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

function removeListeners(element) {
  const newElement = element.cloneNode(true);
  element.parentNode.replaceChild(newElement, element);
  return newElement;
}

const avatarInput = document.getElementById("avatar-input");
const imageBox = document.getElementById("image-box");
let avatarClear = document.getElementById("avatar-clear");
const croppedImageData = document.getElementById("cropped-image-data");
avatarInput.addEventListener("change", () => {
  const imgFile = avatarInput.files[0];
  const imgUrl = URL.createObjectURL(imgFile);

  imageBox.innerHTML = `<img id="image-cropper" class="hidden" src=${imgUrl} />`;
  avatarClear.classList.remove("hidden");
  avatarInput.classList.add("hidden");

  const image = document.getElementById("image-cropper");
  const cropper = new Cropper(image, {
    aspectRatio: 1 / 1,
  });

  avatarClear = removeListeners(avatarClear);
  avatarClear.addEventListener("click", (e) => {
    console.log("clicked");
    e.preventDefault();

    imageBox.innerHTML = "";
    avatarClear.classList.add("hidden");
    avatarInput.classList.remove("hidden");

    avatarInput.value = "";
  });
});
