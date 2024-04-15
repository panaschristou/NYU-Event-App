const csrftoken = $('meta[name="csrf-token"]').attr("content");
const avatarInput = document.getElementById("avatar-input");
const imageBox = document.getElementById("image-box");
let avatarClear = document.getElementById("avatar-clear");
let avatarSave = document.getElementById("avatar-save");
let formSubmit = $(".profile-form-submit")[0];
const croppedImageData = document.getElementById("cropped-image-data");
const avatarMessage = document.getElementById("avatar-message");

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

const removeListeners = (element) => {
  const newElement = element.cloneNode(true);
  element.parentNode.replaceChild(newElement, element);
  return newElement;
};

const switchOffCropperUI = () => {
  imageBox.innerHTML = "";
  avatarInput.classList.remove("hidden");
  avatarClear.classList.add("hidden");
  avatarSave.classList.add("hidden");
};

avatarInput.addEventListener("change", () => {
  const imgFile = avatarInput.files[0];
  const imgUrl = URL.createObjectURL(imgFile);

  // switch on cropper UI
  imageBox.innerHTML = `<img id="image-cropper" class="hidden" src=${imgUrl} />`;
  avatarClear.classList.remove("hidden");
  avatarSave.classList.remove("hidden");
  avatarInput.classList.add("hidden");

  const image = document.getElementById("image-cropper");
  const cropper = new Cropper(image, {
    aspectRatio: 1 / 1,
  });
  let savedCropper = null;

  avatarClear = removeListeners(avatarClear);
  avatarClear.addEventListener("click", (e) => {
    switchOffCropperUI();
    savedCropper = null;
    avatarMessage.classList.add("hidden");
  });

  avatarSave = removeListeners(avatarSave);
  avatarSave.addEventListener("click", (e) => {
    switchOffCropperUI();
    savedCropper = cropper;
    avatarMessage.classList.remove("hidden");
  });

  formSubmit = removeListeners(formSubmit);
  formSubmit.addEventListener("click", (e) => {
    savedCropper.getCroppedCanvas().toBlob((blob) => {
      const fd = new FormData();
      fd.append("file", blob);
      fetch(`avatar`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrftoken,
        },
        body: fd,
      })
        .then((response) => response.json())
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });

  // force avatarInput listener to catch change even when users are submitting the same file
  avatarInput.value = null;
});
