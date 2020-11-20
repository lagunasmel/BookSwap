function confirmRemoveBook(book) {
    var x = document.getElementById(book);
    console.log(x)
    x.style.display = "block";
}

function modalDismiss(book) {
    var x = document.getElementById(book);
    console.log(x)
    x.style.display = "none";
}