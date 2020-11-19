// Event handler for "add to wishlist"
function addToWishlist(book)
/* 
 * AddToWishlist  populates and shows the modal asking if the user
 *  really wants to add the book to their wishlist.
 * Accepts:
 *  book (object):  Book in question
 * Returns:
 *  Null
 */
{
    event.preventDefault();
    // Fill book info
    $('#addToWishlistModalTitle').text(book['title']);
    $('#addToWishlistModalAuthor').text(book['author']);
    $('#addToWishlistModalISBN').text(book['ISBN']);
    $('#addToWishlistModalCopyQuality').text(book['copyQuality']);
    $('#addToWishlistModalPointsNeeded').text(book['pointsNeeded']);
    $('#addToWishlistModalListingUser').text(book['listingUser']);
    $('#addToWishlistModalTimeHere').text(book['timeHere']);
    $('#addToWishlistModal').modal("show");

    // craete event handler attribute for "Confirm Button"
    var ISBN = book["ISBN"];
    $("#addToWishlistModalConfirmAddToWishlist").attr('action', '/addToWishlist/' + ISBN);
}


// Event handler for "Request Trade"
function requestTrade(book, points)
/*
 * RequestTrade populates and shows the modal either informing the user they
 *  do not have sufficient points, or asking for trade request confirmation.
 * Accepts:
 *  book (object):  Book in question
 * Returns:
 *  Null
 */
{
    event.preventDefault();
    if (points - book['pointsNeeded'] >= 0)
    {
        $('#requestTradeModalTitle').text(book['title']);
        $('#requestTradeModalAuthor').text(book['author']);
        $('#requestTradeModalUsername').text(book['listingUser']);
        var pointsNeeded = book['pointsNeeded'];
        if (pointsNeeded != 1)
            pointsNeeded += " points";
        else
            pointsNeeded += " point";
        $('#requestTradeModalPointsNeeded').text(pointsNeeded);
        var pointsRemaining = points - book['pointsNeeded'];
        if (pointsRemaining != 1)
            pointsRemaining += " points";
        else
            pointsRemaining += " point";
        $('#requestTradeModalPointsRemaining').text(pointsRemaining);
        $('#requestTradeModal').modal('show');
    }
    else
    {
        $('#requestTradeInsufficientPointsModalUsername').
            text(book['listingUser']);
        var pointsNeeded = book['pointsNeeded'];
        if (pointsNeeded != 1)
            pointsNeeded += " points"
        else
            pointsNeeded += " point"
        $('#requestTradeInsufficientPointsModalPointsNeeded').
            text(pointsNeeded);
        $('#requestTradeInsufficientPointsModalTitle').
            text(book['title']);
        var pointsAvailable = points;
        if (pointsAvailable != 1)
            pointsAvailable += " points"
        else
            pointsAvailable += " point"
        $('#requestTradeInsufficientPointsAvailable').
            text(pointsAvailable)
        
        $('#requestTradeInsufficientPointsModal').modal('show');
    }
}


