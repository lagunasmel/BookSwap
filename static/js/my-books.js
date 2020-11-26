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
        let points = $('#pointsBookId' + bookId).val();
        addBook(bookId, quality, points);
    });
    $('#confirmBtnBookId' + bookId).show();
    $('#cancelBtnBookId' + bookId).show();
    console.log(bookId);
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
            'request': 'my-books'
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

function addBookTemplate(url, bookId, quality, points) {
    $.ajax(url, {
        contentType: "application/json",
        data: JSON.stringify({
            'isbn': $('#newBookISBN').val(),
            'quality': quality,
            'bookId': bookId,
            'points': points,
            'request': 'my-books'
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

function modalDismiss(bookID) {
    var x = document.getElementById(bookID);
    console.log(x)
    x.style.display = "none";
}

function confirmChangePoints(title, points, id)
/*
 * ConfirmChangePoints brings up modal asking user if they want to change
 *  points, or not.
 * Accepts:
 *  title (string): Book title
 *  points (int): Current book points value
 *  id (int): UserBooks id value
 */ {
    $('#changePointsModalTitle').text(title);
    var newPoints = points;
    if (newPoints == 1)
        newPoints += " point";
    else
        newPoints += " points";
    $('#changePointsModalNewPoints').val(points);
    $('#changePointsModalPoints').text(newPoints);

    $('#changePointsModalButton').on('click', function () {
        changePoints($('#changePointsModalNewPoints').val(), id);

    });
    $('#changePointsModal').modal("show");
}


function changePoints(points, id) {
    $.ajax('/change-points', {
        contentType: "application/json",
        data: JSON.stringify({
            'id': id,
            'points': points
        }),
        type: 'POST',
        success: function (data) {
            location.reload(true);
        }
    });
}