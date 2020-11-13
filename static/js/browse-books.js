$("#bookSearchFormButton").on("click", function() {
  event.preventDefault();
  $("#recent-additions").hide();
  $("#bookSearch").hide();
  $("#bookSearchResults").show();
  alert("Button clicked");
  });
