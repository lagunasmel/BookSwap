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
    $("#searchResults").hide();
    $("#listBook").show();
}

function searchBookTemplate(url) {
    $("#listBook").hide();
    $("#pendingSearch").show();
    $.ajax(url, {
        contentType: "application/json",
        data: JSON.stringify({
            'isbn': $('#newBookISBN').val(),
            'author': $('#newBookAuthor').val(),
            'title': $('#newBookTitle').val(),
            'request': 'search'
        }),
        type: 'POST',
        success: function (data) {
            $("#pendingSearch").hide();
            $("#searchResultsInner").html(data);
            $("#searchResults").show();
        }
    })
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