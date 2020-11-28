function confirmRemoveBook(book) {
    $("#removeBookModalTitle").text(book['title']);
    $("#bookRem").attr("value", book['title']);
    $("#wishlistRem").attr("value", book['wishlistId']);
    $("#removeBookModal").modal("show");
}

function searchBookTemplate(url) {
    $("#wishlistSearch").hide();
    $("#pendingSearch").show();
    $.ajax(url, {
        contentType: "application/json",
        data: JSON.stringify({
            'isbn': $('#newBookISBN').val(),
            'author': $('#newBookAuthor').val(),
            'title': $('#newBookTitle').val(),
            'request': 'my-wishlist'
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

function cancelAddBook() {
    $("#confirmBook").hide();
    $("#searchResults").hide();
    $("#listBook").show();
    $('#wishlistSearch').show();
}

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
        addBook(bookId);
    });
    $('#confirmBtnBookId' + bookId).show();
    $('#cancelBtnBookId' + bookId).show();
    console.log(bookId);
}

function addBookTemplate(url, bookId) {
    $.ajax(url, {
        contentType: "application/json",
        data: JSON.stringify({
            'isbn': $('#newBookISBN').val(),
            'bookId': bookId,
            'request': 'my-wishlist'
        }),
        type: 'POST',
        success: function (data) {
            let newDoc = document.open("text/html", "replace");
            newDoc.write(data);
            newDoc.close();
        }
    });
}

function seeCopies(book)
/*****************************************************************************\
 * SeeCopies sends a request for copies of a particular book to database,
 *  and uses response to populate a modal.
 * Accepts:
 *  book (object(: JSON-ified copy of book dictionary
 * Returns:
 *  Null
 \*****************************************************************************/ {
    event.preventDefault();
    //Make table.  We make the entire body via DOM, since we clear it to confirm
    //  trade requests.
    $('#showCopiesModalBody').empty();
    var footer = $('#showCopiesModalFooter');
    footer.empty();
    var leadText;
    if (book['numberAvailable'] == 1) {
        leadText = "This is the 1 copy ";
    } else {
        leadText = `These are the ${book['numberAvailable']} copies `;
    }
    leadText += "our users currently have on offer:";
    $('<p/>').text(leadText).appendTo($('#showCopiesModalBody'));
    let copiesTable = $('<table/>')
        .addClass("table table-hover")
        .appendTo($('#showCopiesModalBody'));
    let copiesTableHead = $('<thead/>').appendTo(copiesTable);
    let headRow = $('<tr/>').appendTo(copiesTableHead);
    $('<th/>').attr("scope", "col").text("Username").appendTo(headRow);
    $('<th/>').attr("scope", "col").text("Copy Quality").appendTo(headRow);
    $('<th/>').attr("scope", "col").text("Point Cost").appendTo(headRow);
    $('<th/>').attr("scope", "col").text("Request Trade").appendTo(headRow);
    let tableBody = $('<tbody/>').attr('id', 'showCopiesModalTableBody')
        .appendTo(copiesTable);

    let data = {"request": "copiesModal", "book": JSON.stringify(book)};
    $.ajax({
        url: '/wishlist',
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function (data) {
            title = data['title'];
            $('#showCopiesModalTitle').text(title);
            $('#showCopiesModalNumber').text(data['count']);
            var copies = data['copies'];
            $('#showCopiesModalCover').attr("src", copies[0]['coverImageUrl']);
            $.each(copies, function(i)
                {
                    var row = $('<tr/>').appendTo(tableBody);
                    var col1 = $('<td/>')
                        .text(copies[i]['username'])
                        .appendTo(row);
                    var col2 = $('<td/>')
                        .text(copies[i]['qualityDescription'])
                        .appendTo(row);
                    var col3 = $('<td/>')
                        .text(copies[i]['points'])
                        .appendTo(row);
                    var col4 = $('<td/>')
                        .appendTo(row);
                    var button = $('<button/>')
                        .attr("type", "button")
                        .addClass("btn btn-primary btn-sm")
                        .on("click", function() {
                            requestBook(copies[i], data['points_available'], book)
                        })
                        .text("Request This Book")
                        .appendTo(col4);
                    if (data['points_available'] < copies[i]['points'])
                    {
                        button.prop('disabled', true);
                        button.html("Need More Points");
                    }
                });
            var closeButton = $('<button/>')
                    .attr("type", "button")
                    .addClass("btn btn-secondary btn-sm")
                    .attr("data-dismiss", "modal")
                    .text("Close")
                    .appendTo(footer);

            $('#showCopiesModal').modal("show");
        }
    });
}

function requestBook(book, pointsAvailable, bookTable)
/*****************************************************************************\
 * ReqwestBook changes the copiesModal to represent the User's desire to
 *  request a trade.
 * Accepts:
 *  book (object): UserBooks information
 *  pointsAvailable (number): User's points available
 *  bookTable (object): Books information -- passed just so it can be sent back
 *      if necessary.
 * Returns:
 *  Null
 \****************************************************************************/ {
    var body = $('#showCopiesModalBody');
    body.empty();
    var footer = $('#showCopiesModalFooter');
    footer.empty();
    var bodyHeader = $('<h2/>').text("Confirm Trade Request")
        .appendTo(body);
    $('<p/>').text(`You are about to request ${book['title']} by ${book['author']}`)
        .appendTo(body);
    $('<p/>').text(`You will be requesting this book from user ${book['username']}`)
        .appendTo(body);
    var pointsText = "This will cost you ";
    if (book['points'] == 1) {
        pointsText += "1 point";
    } else {
        pointsText += `${book['points']} points`;
    }
    $('<p/>').text(pointsText).appendTo(body);
    var remainPoints = pointsAvailable - book['points'];
    var remainPointsText = "This will leave you with ";
    if (remainPoints == 1) {
        remainPointsText += "1 point";
    } else {
        remainPointsText += `${remainPoints} points`;
    }
    $('<p/>').text(remainPointsText).appendTo(body);
    var yesButton = $('<button/>')
            .attr("type", "button")
            .addClass("btn btn-primary btn-sm")
            .on("click", function() {
                requestConfirmed(book);
            })
            .text("Yes, Request This Trade")
            .appendTo(footer);
    var noButton = $('<button/>')
            .attr("type", "button")
            .addClass("btn btn-secondary btn-sm")
            .on("click", function() {
                seeCopies(bookTable);
            })
            .text("No, Show All Copies")
            .appendTo(footer);
    var closeButton = $('<button/>')
            .attr("type", "button")
            .addClass("btn btn-secondary btn-sm")
            .attr("data-dismiss", "modal")
            .text("Close")
            .appendTo(footer);
}

function requestConfirmed(book)
/*****************************************************************************\
 * RequestConfirmed sends a trade request order to the App.
 * Accepts:
 *  book (object): UsersBooks entry
 * Returns:
 *  Null
 \****************************************************************************/
{
    event.preventDefault();
    book['pointsNeeded'] = book['points'];
    $.ajax({
        url: '/request-book',
        type: 'POST',
        data: JSON.stringify(book),
        dataType: 'json',
        success: function (data) {
            if (data['success'] == "True") {
                $('#requestTradeSuccessModalTitle').text(data['book']['title']);
                $('#requestTradeSuccessModalUsername').text(data['book']['username']);
                var pointsNeeded = data['book']['pointsNeeded'];
                if (pointsNeeded != 1)
                    pointsNeeded += " points"
                else
                    pointsNeeded += " point"
                $('#requestTradeSuccessModalPointsNeeded').text(pointsNeeded);
                var pointsAvailable = data['points_available'];
                if (pointsAvailable != 1)
                    pointsAvailable += " points";
                else
                    pointsAvailable += " point";
                $('#requestTradeSuccessModalPointsAvailable').text(pointsAvailable);
                $('#requestTradeSuccessModal').modal({
                    backdrop: 'static',
                    keyboard: false
                });
                $('#showCopiesModal').modal("hide");
                $('#requestTradeSuccessModal').modal("show");
            } else {
                location.reload(true);
            }
        }
    });

}
