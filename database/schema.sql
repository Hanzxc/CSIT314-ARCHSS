-- Tables for Sprint 1 (US1 - US6)
-- Column names are the same as the attribute names in the entity classes

CREATE TABLE IF NOT EXISTS user_profile (
    profileId    INTEGER PRIMARY KEY AUTOINCREMENT,
    profileName  TEXT NOT NULL UNIQUE COLLATE NOCASE,   -- 3-50 chars, capitals don't matter
    description  TEXT DEFAULT '',
    permissions  TEXT NOT NULL,                         -- JSON list e.g. ["Manage user accounts"]
    status       TEXT NOT NULL DEFAULT 'Active'         -- 'Active' or 'Suspended'
);

CREATE TABLE IF NOT EXISTS user_account (
    userId       INTEGER PRIMARY KEY AUTOINCREMENT,
    username     TEXT NOT NULL UNIQUE,
    password     TEXT NOT NULL,                         -- sha256 hash, never plain text
    fullName     TEXT NOT NULL,
    email        TEXT,
    phone        TEXT,
    profileId    INTEGER NOT NULL REFERENCES user_profile(profileId),
    status       TEXT NOT NULL DEFAULT 'Active',        -- 'Active' or 'Suspended'
    createdDate  TEXT DEFAULT CURRENT_TIMESTAMP
);
