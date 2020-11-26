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
            var requestModalTableBody=$('#showCopiesModalTableBody');
            requestModalTableBody.empty();
            var copies = data['copies'];
            $('#showCopiesModalCover').attr("src", copies[0]['coverImageUrl']);
            $.each(copies, function(i)
                {
                    var row = $('<tr/>').appendTo(requestModalTableBody);
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
                            requestBook(copies[i])
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

function requestBook(book)
{
    alert("Book Requested"+ book['userBooksId']);
}
