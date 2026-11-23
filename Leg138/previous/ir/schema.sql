PRAGMA foreign_keys = ON;
CREATE TABLE section (
    section_id TEXT PRIMARY KEY,
    ordinal INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    first_printed_page INTEGER
);
CREATE TABLE item (
    item_id TEXT PRIMARY KEY,
    section_id TEXT NOT NULL REFERENCES section,
    kind TEXT NOT NULL,
    number INTEGER,
    title TEXT NOT NULL,
    locator TEXT NOT NULL,
    available TEXT NOT NULL,
    data_note TEXT NOT NULL,
    caption_reading TEXT
);
CREATE TABLE source (
    path TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    url TEXT NOT NULL,
    bytes INTEGER NOT NULL,
    sha256 TEXT NOT NULL CHECK(length(sha256) = 64),
    data_note TEXT NOT NULL,
    member TEXT,
    package TEXT,
    row_count INTEGER
);
CREATE TABLE item_source (
    item_id TEXT NOT NULL REFERENCES item,
    path TEXT NOT NULL REFERENCES source,
    role TEXT NOT NULL,
    PRIMARY KEY (item_id, path, role)
);
CREATE TABLE section_source (
    section_id TEXT NOT NULL REFERENCES section,
    path TEXT NOT NULL REFERENCES source,
    PRIMARY KEY (section_id, path)
);
CREATE TABLE location (
    item_id TEXT NOT NULL REFERENCES item,
    part INTEGER NOT NULL,
    path TEXT NOT NULL REFERENCES source,
    printed_page INTEGER,
    pdf_page INTEGER NOT NULL,
    pdf_rect TEXT,
    pixel_rect TEXT,
    companion_file TEXT,
    role TEXT NOT NULL,
    PRIMARY KEY (item_id, part)
);
CREATE TABLE dataset (
    sql_name TEXT PRIMARY KEY,
    csv_path TEXT NOT NULL UNIQUE,
    row_count INTEGER NOT NULL,
    description TEXT NOT NULL
);
CREATE TABLE item_dataset (
    item_id TEXT NOT NULL REFERENCES item,
    sql_name TEXT NOT NULL REFERENCES dataset,
    role TEXT NOT NULL,
    PRIMARY KEY (item_id, sql_name)
);
CREATE TABLE editorial_note (
    item_id TEXT NOT NULL REFERENCES item,
    locator TEXT NOT NULL,
    detail TEXT NOT NULL,
    PRIMARY KEY (item_id, locator, detail)
);
CREATE TABLE report_page (
    printed_page INTEGER PRIMARY KEY,
    pdf_page INTEGER NOT NULL,
    path TEXT NOT NULL REFERENCES source,
    page_group TEXT NOT NULL
);
CREATE TABLE original_table_text (
    path TEXT PRIMARY KEY REFERENCES source,
    contents BLOB NOT NULL
);
CREATE INDEX idx_source_kind ON source(kind);
CREATE INDEX idx_item_section ON item(section_id);
CREATE INDEX idx_item_source_path ON item_source(path);
CREATE VIEW report_catalogue AS
SELECT s.ordinal AS section_order, s.title AS section, i.item_id, i.kind, i.number,
       i.title, i.locator, i.available, i.data_note
FROM item AS i JOIN section AS s USING(section_id);
CREATE VIEW open_page AS
SELECT l.item_id, l.part, l.role, l.printed_page, l.pdf_page,
       s.url || '#page=' || l.pdf_page AS pdf_url, l.pdf_rect, l.companion_file
FROM location AS l JOIN source AS s USING(path);
CREATE VIEW chapter_files AS
SELECT c.ordinal AS section_order, c.title AS section, s.path, s.kind, s.data_note,
       s.url, s.package, s.member, s.row_count
FROM section_source AS a JOIN section AS c USING(section_id) JOIN source AS s USING(path);
