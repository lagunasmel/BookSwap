// Check that new password confirm matches new password
$("#new-password-confirm").keyup(function () {
    if ($("#new-password").val() !== $(this).val()) {
        $(this).removeClass("is-valid").addClass("is-invalid");
    } else {
        $(this).removeClass("is-invalid").addClass("is-valid");
    }
});

$("#new-password").on("keyup", function () {
    if ($("#new-password-confirm").val()) {
        if ($(this).val() !== $("#new-password-confirm").val()) {
            $("#new-password-confirm").removeClass("is-valid").addClass("is-invalid");
        } else {
            $("#new-password-confirm").removeClass("is-invalid").addClass("is-valid");
        }
    }
});

// Send off user info change
function changeUserInformationTemplate(url) {
    $.ajax(url, {
        contentType: "application/json",
        data: JSON.stringify({
            // First key:value is flag for request
            "request": "changeUserSettings",
            // Other key:value pairs are user data
            "username": $("#userHomeAccountChangeUsername").val(),
            "email": $("#userHomeAccountChangeEmail").val(),
            "fName": $("#userHomeAccountChangefName").val(),
            "lName": $("#userHomeAccountChangelName").val(),
            "streetAddress": $("#userHomeAccountChangeStreetAddress").val(),
            "city": $("#userHomeAccountChangeCity").val(),
            "state": $("#userHomeAccountChangeState").val(),
            "postCode": $("#userHomeAccountChangePostCode").val()
        }),
        type: "POST",
        success: function (account_settings) {
            $('#userHomeAccountChangeModal').modal("hide");
            let newDoc = document.open("text/html", "replace");
            newDoc.write(account_settings);
            newDoc.close();
            // location.reload(true);
        }
    });
}

// Send off password info change
function changePasswordTemplate(url, username) {
    if (($("#new-password").val() === "") ||
        ($("#new-password").val() != $("#new-password-confirm").val())) {
        alert(`Please make sure you enter a new password, and that you
    enter the same new password twice.`);
    } else {
        $.ajax(url, {
            contentType: "application/json",
            data: JSON.stringify({
                // First key:value is flag for request
                "request": "changePassword",
                // Other key:value pairs are user data
                "username": username,
                "oldPassword": $("#old-password").val(),
                "newPassword": $("#new-password").val()
            }),
            type: "POST",
            success: function (account_settings) {
                if (account_settings['passwordMismatch'])
                    $("#old-password").val("");
                else {
                    $("#userHomePasswordChangeModal").modal("hide");
                    let newDoc = document.open("text/html", "replace");
                    newDoc.write(account_settings);
                    newDoc.close();
                }
            }
        });
    }
}
