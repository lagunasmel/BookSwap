function confirmRemoveBook(book) {
    $("#removeBookModalTitle").text(book['title']);
    $("#bookRem").attr("value", book['title']);
    $("#wishlistRem").attr("value", book['wishlistId']);
    $("#removeBookModal").modal("show");
}

function seeCopies(book)
/*****************************************************************************\
 * SeeCopies sends a request for copies of a particular book to database,
 *  and uses response to populate a modal.
 * Accepts:
 *  book (object(: JSON-ified copy of book dictionary
 * Returns:
 *  Null
\*****************************************************************************/
{
    event.preventDefault();
    //Make table.  We make the entire body via DOM, since we clear it to confirm
    //  trade requests.
    $('#showCopiesModalBody').empty();
    $('#showCopiesModalFooterLeft').empty();
    var leadText;
    if (book['numberAvailable'] == 1)
    {
        leadText = "This is the 1 copy ";
    }
    else
    {
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
    let tableBody= $('<tbody/>').attr('id', 'showCopiesModalTableBody')
                .appendTo(copiesTable);

    let data = {"request": "copiesModal", "book": JSON.stringify(book)};
    $.ajax({
        url:'/wishlist',
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
 \****************************************************************************/
{
    var body = $('#showCopiesModalBody');
    body.empty();
    var leftFooter = $('#showCopiesModalFooterLeft');
    leftFooter.empty();
    var bodyHeader = $('<h2/>').text("Confirm Trade Request")
        .appendTo(body);
    $('<p/>').text(`You are about to request ${book['title']} by ${book['author']}`)
        .appendTo(body);
    $('<p/>').text(`You will be requesting this book from user ${book['username']}`)
        .appendTo(body);
    var pointsText = "This will cost you ";
    if (book['points'] == 1)
    {
        pointsText += "1 point";
    }
    else
    {
        pointsText += `${book['points']} points`;
    }
    $('<p/>').text(pointsText).appendTo(body);
    var remainPoints = pointsAvailable - book['points'];
    var remainPointsText = "This will leave you with ";
    if (remainPoints == 1)
    {
        remainPointsText += "1 point";
    }
    else
    {
        remainPointsText += `${remainPoints} points`;
    }
    $('<p/>').text(remainPointsText).appendTo(body);
    var yesButton = $('<button/>')
            .attr("type", "button")
            .addClass("btn btn-primary btn-sm")
            .on("click", function() {
                requestConfirmed(book);
            })
            .text("Yes")
            .appendTo(leftFooter);
    var noButton = $('<button/>')
            .attr("type", "button")
            .addClass("btn btn-secondary btn-sm")
            .on("click", function() {
                seeCopies(bookTable);
            })
            .text("No")
            .appendTo(leftFooter);
}
