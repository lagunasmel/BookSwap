function confirmBook(e, btnId) {
    // btnId is in the format 'addBtnBookIdXXX' where XXX is the Books table ID value
    console.log(e.target.textContent);
    let bookId = $('#' + btnId).data('bookid');
    $('#' + btnId).hide();
    $('#cancelBtnBookId' + bookId).on('click', () => {
        $('#cancelBtnBookId' + bookId).hide();
        $('#confirmBtnBookId' + bookId).hide();
        $('#addBtnBookId' + bookId).show();
    });
    $('#confirmBtnBookId' + bookId).on('click', () => {
        let quality = $('#copyQualityBookId' + bookId).val();
        addBook(bookId, quality);
    });
    $('#confirmBtnBookId' + bookId).show();
    $('#cancelBtnBookId' + bookId).show();
    console.log(bookId);


    // $("#listBook").hide();
    // $("#confirmBook").show();
    // $("#confirmBookISBN").html(
    //     "ISBN: " + $("#newBookISBN").val()
    // );
    // $("#confirmBookcopyQuality").html(
    //     "Copy Quality: " + $("#newBookQuality option:selected").text()
    // );
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
            $('.add-book-button').each((i, obj) => {
                obj.addEventListener("click", (e) => {
                    confirmBook(e, obj.id);
                });
            });
            $('.confirm-book-button').hide();
            $('.cancel-book-button').hide();
            $("#searchResults").show();
        }
    })
}

function addBookTemplate(url, bookId, quality) {
    $.ajax(url, {
        contentType: "application/json",
        data: JSON.stringify({
            'isbn': $('#newBookISBN').val(),
            'quality': quality,
            'bookId': bookId,
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

function confirmRemoveBook(bookID) {
    var x = document.getElementById(bookID);
    console.log(x)
    x.style.display = "block";
}