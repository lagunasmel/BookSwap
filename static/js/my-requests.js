// event handler for "cancel" button
function cancelTradeRequest(book)
/*
 * CancelTradeRequest displays the modal asking for confirmation that the
 *  user wants to cancel the trade.
 * acepts:
 *  book (object):  userbooks book in question
 * returns:
 *  null
 */
{
    event.preventDefault();
    $('#cancelModalTitle').text(book['title']);
    $('#cancelModalAuthor').text(book['author']);
    $('#cancelModalISBN').text(book['isbn']);
    $('#cancelModalUsername').text(book['username']);
    points = book['points'];
    if (points == 1)
        points += " point";
    else
        points += ' points';
    $('#cancelModalPoints').text(points);
    $('#cancelModalCover').attr('src', book['coverImageUrl']);
    $('#cancelModalConfirmForm').attr('action', '/cancel-request/' + book['userBooksId']);
    $('#cancelModal').modal('show');
}


