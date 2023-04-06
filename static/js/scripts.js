// Get the modal element
var modal = document.getElementById("modal");

// Get the div ellement for blur effect
var contentContainer = document.querySelector(".content-container");

// Get the button that opens the modal
var btn = document.getElementById("openModal");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal
btn.onclick = function() {
    contentContainer.classList.add("blur"); 
    modal.style.display = "block";
  
};

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
  contentContainer.classList.remove("blur");
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
    contentContainer.classList.remove("blur");
  }
};

