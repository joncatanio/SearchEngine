-- All unique words found by the crawler
--    id   - primary key
--    word - the word itself
CREATE TABLE Words (
   id   INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   word VARCHAR(64) NOT NULL UNIQUE
);

-- All unique links found by the crawler
--    id    - primary key
--    link  - the link itself
--    title - the most likely title of the page linked by `link`
CREATE TABLE Links (
   id    INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   link  VARCHAR(255) NOT NULL UNIQUE,
   title VARCHAR(512) NOT NULL
);

-- Information about each word
--    wordId   - the id of a word from the Words table
--    linkId   - the link of the page that the word was found on
--    position - the position of the word in the overall text of the page
CREATE TABLE WordMeta (
   wordId   INT UNSIGNED REFERENCES Words(id),
   linkId   INT UNSIGNED REFERENCES Links(id),
   position INT UNSIGNED NOT NULL
);

-- Relation of each link to one another
--    baselink  - the base page containing `hyperlink`
--    hyperlink - the link that was linked from `baselink`
CREATE TABLE Hyperlinks (
   baselink  INT UNSIGNED REFERENCES Links(id),
   hyperlink INT UNSIGNED REFERENCES Links(id)
);

CREATE INDEX WordIndex ON Words(word);
CREATE INDEX LinkIndex ON Links(link);
CREATE INDEX BaselinkIndex ON Hyperlinks(baselink);
CREATE INDEX HyperlinkIndex ON Hyperlinks(hyperlink);
