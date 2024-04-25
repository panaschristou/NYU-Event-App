const csrftoken = $('meta[name="csrf-token"]').attr("content");
const avatarInput = document.getElementById("avatar-input");
const imageBox = document.getElementById("image-box");
let avatarClear = document.getElementById("avatar-clear");
let avatarSave = document.getElementById("avatar-save");
let formSubmit = $(".profile-form-submit")[0];
const croppedImageData = document.getElementById("cropped-image-data");
const avatarMessage = document.getElementById("avatar-message");
const avatarError = document.getElementById("avatar-error");
const MB = 1048576;

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
  const fileName = avatarInput.value.replace("C:\\fakepath\\", ""); // This fake path should be the same across OSes

  avatarError.innerHTML = "";

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
    avatarMessage.innerHTML = "";
  });

  avatarSave = removeListeners(avatarSave);
  avatarSave.addEventListener("click", (e) => {
    cropper.getCroppedCanvas().toBlob((blob) => {
      if (blob.size >= MB) {
        avatarError.innerHTML = "Images of more than 1 MB are not supported.";
        return;
      }
      switchOffCropperUI();
      savedCropper = cropper;
      avatarMessage.innerHTML = fileName + " has been loaded";
    });
  });

  formSubmit = removeListeners(formSubmit);
  formSubmit.addEventListener("click", (e) => {
    if (!savedCropper) return;
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
