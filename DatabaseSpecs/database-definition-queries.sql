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
Drop prior tables.
 */

DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS CopyQualities;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS TradeStatuses;
DROP TABLE IF EXISTS Trades;
DROP TABLE IF EXISTS Wishlists;
DROP TABLE IF EXISTS WishlistsBooks;
DROP TABLE IF EXISTS UserBooks;

/*
Queries that initialize the tables.
 */

-- Books
CREATE TABLE IF NOT EXISTS Books
(
    id            INTEGER NOT NULL PRIMARY KEY,
    title         TEXT    NOT NULL,
    author        TEXT    NOT NULL,
    ISBN          INTEGER,
    OLWorkKey     TEXT UNIQUE,
    OLEditionKey  TEXT UNIQUE,
    coverImageUrl TEXT,
    externalLink  TEXT
);

-- CopyQualities
CREATE TABLE IF NOT EXISTS CopyQualities
(
    id                 INTEGER      NOT NULL PRIMARY KEY,
    qualityDescription VARCHAR(255) NOT NULL
);

-- Users
CREATE TABLE IF NOT EXISTS Users
(
    id            INTEGER      NOT NULL PRIMARY KEY,
    username      VARCHAR(255) NOT NULL UNIQUE,
    email         TEXT         NOT NULL UNIQUE,
    password      VARCHAR(255) NOT NULL,
    fName         VARCHAR(255) NOT NULL,
    lName         VARCHAR(255) NOT NULL,
    streetAddress VARCHAR(255) NOT NULL,
    city          VARCHAR(255) NOT NULL,
    state         VARCHAR(255) NOT NULL,
    postCode      VARCHAR(255) NOT NULL,
    dateCreated   DATETIME     DEFAULT current_timestamp,
    points        FLOAT(32, 1) DEFAULT 0.0
);

-- TradeStatuses
CREATE TABLE IF NOT EXISTS TradeStatuses
(
    id                INTEGER      NOT NULL PRIMARY KEY,
    statusDescription VARCHAR(255) NOT NULL
);

-- Trades
CREATE TABLE IF NOT EXISTS Trades
(
    id              INTEGER NOT NULL PRIMARY KEY,
    userRequestedId INTEGER,
    userBookId      INTEGER,
    statusId        INTEGER,
    dateInitiated   DATETIME DEFAULT current_timestamp,
    dateCompleted   DATETIME DEFAULT NULL,
    FOREIGN KEY (userRequestedId) REFERENCES Users (id) ON DELETE NO ACTION ON UPDATE CASCADE,
    FOREIGN KEY (userBookId) REFERENCES UserBooks (id) ON DELETE NO ACTION ON UPDATE CASCADE,
    FOREIGN KEY (statusId) REFERENCES TradeStatuses (id) ON DELETE NO ACTION ON UPDATE CASCADE
);

-- Wishlists
CREATE TABLE IF NOT EXISTS Wishlists
(
    id          INTEGER NOT NULL PRIMARY KEY,
    userId      INTEGER,
    dateCreated DATETIME DEFAULT current_timestamp,
    FOREIGN KEY (userId) REFERENCES Users (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- WishlistBooks -- Intersection for Wishlists and Books
CREATE TABLE IF NOT EXISTS WishlistsBooks
(
    wishlistId  INTEGER,
    bookId      INTEGER,
    dateCreated DATETIME DEFAULT current_timestamp,
    PRIMARY KEY (wishlistId, bookId),
    FOREIGN KEY (wishlistId) REFERENCES Wishlists (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (bookId) REFERENCES Books (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- UserBooks -- Intersection between Users and Books
CREATE TABLE IF NOT EXISTS UserBooks
(
    id            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    userId        INTEGER,
    bookId        INTEGER,
    copyQualityId INTEGER,
    points        INTEGER          DEFAULT 1,
    dateCreated   DATETIME         DEFAULT current_timestamp,
    available     INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (userId) REFERENCES Users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (bookId) REFERENCES Books (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (CopyQualityId) REFERENCES CopyQualities (id) ON DELETE CASCADE ON UPDATE CASCADE
);


/*
Inserting sample data
 */

-- Sample Books
INSERT INTO Books ('title', 'author', 'ISBN', 'coverImageUrl')
VALUES ('Harry Potter and the Sorcerer''s Stone', 'J. K. Rowling', '9781338596700',
        'https://covers.openlibrary.org/b/id/10447552-L.jpg'),
       ('Sula', 'Toni Morrison', '0394480449', 'https://covers.openlibrary.org/b/id/8384008-L.jpg'),
       ('Six of Crows', 'Leigh Bardugo', '9781627795227', 'https://covers.openlibrary.org/b/id/8736828-L.jpg'),
       ('Becoming', 'Michelle Obama', '1524763152', 'https://covers.openlibrary.org/b/id/8565814-L.jpg'),
       ('The House on Mango Street', 'Sandra Cisneros', '1432865056',
        'https://covers.openlibrary.org/b/olid/OL27340489M-M.jpg'),
       ('The Great Gatsby', 'F. Scott Fitzgerald', '0020199600', 'https://covers.openlibrary.org/b/id/8458105-L.jpg'),
       ('Sister Outsider', 'Audre Lorde', '1580911862', 'https://covers.openlibrary.org/b/id/1940446-L.jpg'),
       ('All the Light We Cannot See', 'Anthony Doerr', '9781476746586',
        'https://covers.openlibrary.org/b/id/7322167-L.jpg'),
       ('The Hate U Give', 'Angie Thomas', '006249855X', 'https://covers.openlibrary.org/b/id/8250019-L.jpg'),
       ('Ender''s Game', 'Orson Scott Card', '0812550706', 'https://covers.openlibrary.org/b/id/9255401-L.jpg'),
       ('Everything I Never Told You', 'Celeste Ng', '0349134286', 'https://covers.openlibrary.org/b/id/8407334-L.jpg');

-- Sample Copy Qualities
INSERT INTO CopyQualities ('qualityDescription')
VALUES ('New'),
       ('Like New'),
       ('Very Good'),
       ('Good'),
       ('Fair'),
       ('Poor');

-- Sample "admin" user, for easy login check
INSERT INTO Users('username', 'password', 'email', 'fName', 'lName', 'streetAddress',
                  'city', 'state', 'postCode', 'points')
VALUES ('admin', 'password', 'admin@bookswap.com', 'Admin', 'Istrator', '123 Main Street', 'Springfield',
        'Oregon', '97475', 10),
       ('csearl2', 'nAvtnI', 'csearl2@cdc.gov', 'Cassey', 'Searl', '44681 Pearson Alley',
        'Saint Louis', 'Missouri', '63131', 10);

-- Sample User data from mockaroo.com
INSERT INTO Users ('username', 'password', 'email', 'fName', 'lName', 'streetAddress',
                   'city', 'state', 'postCode')
VALUES ('fpringle0', '5o6RPSL', 'fpringle0@archive.org', 'Filmore', 'Pringle', '99 Ruskin Court',
        'Knoxville', 'Tennessee', '37924'),
       ('khildrup1', 'IuYdId', 'khildrup1@pen.io', 'Kit', 'Hildrup', '82567 Onsgard Road',
        'Richmond', 'Virginia', '23203'),
       ('esabates3', 'kydXrZxzz9Va', 'esabates3@samsung.com', 'Edward', 'Sabates', '63 Welch Court',
        'Spokane', 'Washington', '99215'),
       ('jextal4', 'DUwvKPx81Iji', 'jextal4@reference.com', 'Jason', 'Extal', '98 Sugar Alley',
        'Nashville', 'Tennessee', '37215');

-- Sample Wishlists
INSERT INTO Wishlists (userId)
VALUES (1),
       (2),
       (3),
       (4),
       (5),
       (6)
;

-- Sample Wishlist Books
-- First user wants "Yellow River"
INSERT INTO WishlistsBooks (wishlistId, bookId)
VALUES ((SELECT id
         FROM Wishlists
         WHERE userId = 1
        ),
        (SELECT id FROM Books WHERE ISBN = '99999'));

-- SEcond uesr has no books in their wishlist

-- Third user wants "Forever A Loan" and "Six of Crows"
INSERT Into WishlistsBooks (wishlistId, bookId)
VALUES ((SELECT id FROM Wishlists WHERE userId = 3),
        (SELECT id FROM Books WHERE ISBN = '1111111111111')),
       ((SELECT id FROM Wishlists WHERE userId = 3),
        (SELECT ID FROM BOOKS WHERE ISBN = '9781627795227'))
;

-- Some sample books in UserBooks
-- First user Has 3 books, second user has 1 book, third user has 2 books
INSERT INTO UserBooks (userId, bookId, copyQualityId, points, Available)
VALUES (1, 1, 2, 1, 1),
       (1, 3, 4, 2, 1),
       (1, 2, 3, 3, 1),
       (2, 3, 4, 4, 0),
       (3, 1, 3, 2, 0),
       (3, 7, 1, 3, 1),
       (1, 1, 1, 10, 0),
       (3, 2, 2, 10, 0),
       (2, 3, 3, 10, 0),
       (4, 1, 1, 5, 0),
       (4, 2, 2, 4, 0),
       (4, 8, 3, 3, 1),
       (4, 1, 2, 1, 0),
       (3, 1, 1, 2, 0),
       (2, 2, 3, 1, 0),
       (5, 4, 4, 3, 1),
       (5, 5, 5, 1, 1),
       (5, 6, 5, 2, 1),
       (6, 9, 1, 5, 1),
       (6, 10, 3, 2, 1),
       (1, 11, 1, 3, 1);

-- TradeStatus values
INSERT INTO TradeStatuses (statusDescription)
VALUES ("No Current Trade"),
       ("Trade Requested"),
       ("Trade Accepted -- In Progress"),
       ("Trade Rejected: Rejected By Book Owner"),
       ("Trade Rejected: Rejected By Inaction"),
       ("Trade Completed"),
       ("Trade Marked As Failed");

-- Sample Trades
-- First user has three trades going:  2 pending and 1 accepts:
INSERT INTO Trades (userRequestedId, userBookId, statusId)
VALUES (2, 7, 2),
       (3, 8, 2),
       (4, 9, 3),
       (1, 4, 2),
       (1, 5, 3),
       (1, 10, 4),
       (1, 11, 5),
       (1, 13, 6),
       (1, 14, 7);

-- Insert a trade that is a bit older
INSERT INTO Trades (userRequestedId, userBookId, statusId, dateInitiated)
VALUES (1, 12, 3, "2019-12-02 23:18:04");
