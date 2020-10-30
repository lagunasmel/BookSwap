/*
CS361 OSU Fall 2020
Team: 5++
Members: 
    Phoenix Harris
    Melissa Lagunas
    Alexa Langen
    Ryan McKenzie
    Nishant Tharani
    Ben Wichser
Project Title: Book Swap
*/

/*
Queries that initialize the tables.
*/

-- Books
CREATE TABLE IF NOT EXISTS Books (
    id INTEGER NOT NULL PRIMARY KEY,
    title TEXT NOT NULL,
    ISBN INTEGER NOT NULL,
    cover BLOB
);
    
-- CopyQualities
CREATE TABLE IF NOT EXISTS CopyQualities(
    id INT NOT NULL PRIMARY KEY,
    qualityDescription VARCHAR(255) NOT NULL
);

-- Users
CREATE TABLE IF NOT EXISTS Users(
    id INT NOT NULL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    fName VARCHAR(255) NOT NULL,
    lName VARCHAR(255) NOT NULL,
    streetAddress VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    postCode VARCHAR(255) NOT NULL,
    points INT DEFAULT 0
);

-- TradeStatuses
CREATE TABLE IF NOT EXISTS TradeStatuses(
    id INT NOT NULL PRIMARY KEY,
    statusDescription VARCHAR(255) NOT NULL
);

-- Trades
CREATE TABLE IF NOT EXISTS Trades(
    id INT NOT NULL PRIMARY KEY,
    userRequestedId INT,
    userPostedId INT,
    bookId INT,
    statusId INT,
    FOREIGN KEY (userRequestedId) REFERENCES Users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (userPostedId) REFERENCES Users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (bookId) REFERENCES Books (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (statusId) REFERENCES TradeStatuses (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Wishlists
CREATE TABLE IF NOT EXISTS Wishlists(
    id INT NOT NULL PRIMARY KEY,
    userId INT,
    FOREIGN KEY (userId) REFERENCES Users (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- WishlistBooks -- Intersection for Wishlists and Books
CREATE TABLE IF NOT EXISTS WishlistsBooks(
    wishlistId INT,
    bookId INT,
    PRIMARY KEY (wishlistId, bookId),
    FOREIGN KEY (wishlistId) REFERENCES Wishlists (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (bookId) REFERENCES Books (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- UserBooks -- Intersection between Users and Books
CREATE TABLE IF NOT EXISTS UserBooks(
    userId INT,
    bookId INT,
    PRIMARY KEY (userId, bookId),
    FOREIGN KEY (userId) REFERENCES Users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (bookId) REFERENCES Books (id) ON DELETE CASCADE ON UPDATE CASCADE
);

