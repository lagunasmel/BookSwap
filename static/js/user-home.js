// Check that new password confirm matches new password
$("#new-password-confirm").keyup(function () {
  if ($("#new-password").val() !== $(this).val() || $(this).val().length < 5) 
  {
    $(this).removeClass("is-valid").addClass("is-invalid");
  } else {
    $(this).removeClass("is-invalid").addClass("is-valid");
  }
});

$("#new-password").on("keyup", function () {
  if ($(this).val().length < 5)
  {
    $(this).removeClass("is-valid").addClass("is-invalid")
  }
  else
  {
    $(this).removeClass("is-invalid").addClass("is-valid")
  }
  if ($("#new-password-confirm").val()) {
    if ($(this).val() !== $("#new-password-confirm").val()) {
      $("#new-password-confirm").removeClass("is-valid").addClass("is-invalid");
    } else {
      $("#new-password-confirm").removeClass("is-invalid").addClass("is-valid");
    }
  }
});

// Put correct modal up, and reset password inputs.
function document_ready(show_account_modal, show_password_modal)
{
  if (show_account_modal)
  {
      // alert("Showing account settings modal");
      $('#userHomeAccountChangeModal').modal("show");
  }
  if (show_password_modal)
  {
      // alert("Showing password change modal");
      $('#userHomePasswordChangeModal').modal("show");
  }
  // $('#new-password').removeClass('is-valid').removeClass('is-invalid')
  // $('#new-password-confirm').removeClass('is-valid').removeClass('is-invalid')
}
 
