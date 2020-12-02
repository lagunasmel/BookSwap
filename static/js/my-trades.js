// Event handler for "Reject Request" button
function rejectTradeRequest(book)
/*
 * RejectTradeRequest displays the modal asking for confirmation that the
 *  user wants to reject the trade.
 * Acepts:
 *  book (object):  UserBooks book in question
 * Returns:
 *  Null
 */
{
    event.preventDefault();
    $('#rejectModalTitle').text(book['Title']);
    $('#rejectModalAuthor').text(book['Author']);
    $('#rejectModalISBN').text(book['ISBN']);
    $('#rejectModalUsername').text(book['Requester']);
    points = book['Points'];
    if (points == 1)
        points += " point";
    else
        points += ' points';
    $('#rejectModalPoints').text(points);
    $('#rejectModalCover').attr("src", book['coverImageUrl']);
    $('#rejectModalConfirmForm').attr('action', '/reject-trade/' + book['userBooksId']);
    $('#rejectModal').modal('show');
}

// event handler for "accept request" button
function acceptTradeRequest(book)
/*
 * accepttraderequest displays the modal asking for confirmation that the
 *  user wants to cancel the trade.
 * acepts:
 *  book (object):  userbooks book in question
 * returns:
 *  null
 */
{
    event.preventDefault();
    $('#acceptModalTitle').text(book['Title']);
    $('#acceptModalAuthor').text(book['Author']);
    $('#acceptModalISBN').text(book['ISBN']);
    $('#acceptModalUsername').text(book['Requester']);
    points = book['Points'];
    if (points == 1)
        points += " point";
    else
        points += ' points';
    $('#acceptModalPoints').text(points);
    $('#acceptModalCover').attr("src", book['coverImageUrl']);
    $('#acceptModalConfirmForm').attr('action', '/accept-trade/' + book['userBooksId']);
    $('#acceptModal').modal('show');
}

// event handler for "cancel request" button
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
    $('#cancelModalTitle').text(book['Title']);
    $('#cancelModalAuthor').text(book['Author']);
    $('#cancelModalISBN').text(book['ISBN']);
    $('#cancelModalUsername').text(book['Requester']);
    points = book['Points'];
    if (points == 1)
        points += " point";
    else
        points += ' points';
    $('#cancelModalPoints').text(points);
    $('#cancelModalCover').attr('src', book['coverImageUrl']);
    $('#cancelModalConfirmForm').attr('action', '/reject-trade/' + book['userBooksId']);
    $('#cancelModal').modal('show');
}




