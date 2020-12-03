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

// event handler for "mark as received" button
function receivedTradeRequest(book)
/*
 * ReceivedTradeRequest displays the modal asking for confirmation that the
 *  user wants mark the trade as completed.
 * acepts:
 *  book (object):  userbooks book in question
 * returns:
 *  null
 */
{
    event.preventDefault();
    $('#receivedModalTitle').text(book['title']);
    $('#receivedModalAuthor').text(book['author']);
    $('#receivedModalISBN').text(book['isbn']);
    $('#receivedModalUsername').text(book['username']);
    points = book['points'];
    if (points == 1)
        points += " point";
    else
        points += ' points';
    $('#receivedModalPoints').text(points);
    $('#receivedModalCover').attr('src', book['coverImageUrl']);
    $('#receivedModalConfirmForm').attr('action', '/book-received/' + book['userBooksId']);
    $('#receivedModal').modal('show');
}

// event handler for "mark as received" button
function notReceivedTradeRequest(book)
/*
 * NotReceivedTradeRequest displays the modal asking for confirmation that the
 *  user wants to mark the trade as unfulfilled.
 * acepts:
 *  book (object):  userbooks book in question
 * returns:
 *  null
 */
{
    event.preventDefault();
    $('#notReceivedModalTitle').text(book['title']);
    $('#notReceivedModalAuthor').text(book['author']);
    $('#notReceivedModalISBN').text(book['isbn']);
    $('#notReceivedModalUsername').text(book['username']);
    points = book['points'];
    if (points == 1)
        points += " point";
    else
        points += ' points';
    $('#notReceivedModalPoints').text(points);
    $('#notReceivedModalCover').attr('src', book['coverImageUrl']);
    $('#notReceivedModalConfirmForm').attr('action', '/book-not-received/' + book['userBooksId']);
    $('#notReceivedModal').modal('show');
}

