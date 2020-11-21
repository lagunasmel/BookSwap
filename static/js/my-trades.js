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
        points == ' points';
    $('#rejectModalPoints').text(book['Points']);
    $('#rejectModalConfirmForm').attr('action', '/reject-trade/' + book['userBooksId']);
    $('#rejectModal').modal('show');
}




