function confirmRemoveBook(book) {
    $("#removeBookModalTitle").text(book['title']);
    $("#bookRem").attr("value", book['title']);
    $("#wishlistRem").attr("value", book['wishlistId']);
    $("#removeBookModal").modal("show");
}

function modalDismiss(book) {
    var x = document.getElementById(book);
    console.log(x)
    x.style.display = "none";
}
