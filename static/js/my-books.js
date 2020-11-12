function confirmBook() {
    $("#listBook").hide();
    $("#confirmBook").show();
    $("#confirmBookISBN").html(
        "ISBN: " + $("#newBookISBN").val()
    );
    $("#confirmBookcopyQuality").html(
        "Copy Quality: " + $("#newBookQuality option:selected").text()
    );
}

function cancelAddBook() {
    $("#confirmBook").hide();
    $("#listBook").show();
}

function addBookTemplate(url) {
    $.ajax(url, {
        contentType: "application/json",
        data: JSON.stringify({
            'isbn': $('#newBookISBN').val(),
            'quality': $('#newBookQuality').val(),
            'request': 'add'
        }),
        type: 'POST',
        success: function (data) {
            let newDoc = document.open("text/html", "replace");
            newDoc.write(data);
            newDoc.close();
        }
    });
}