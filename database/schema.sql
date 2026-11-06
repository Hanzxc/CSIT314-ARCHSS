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

-- US14: one company profile per designer account. Existing tables are retained.
CREATE TABLE IF NOT EXISTS company_profile (
    companyId    INTEGER PRIMARY KEY AUTOINCREMENT,
    designerId   INTEGER NOT NULL UNIQUE REFERENCES user_account(userId),
    companyName  TEXT NOT NULL CHECK(length(trim(companyName)) BETWEEN 3 AND 100),
    description  TEXT NOT NULL CHECK(length(trim(description)) BETWEEN 1 AND 2000),
    services     TEXT NOT NULL CHECK(length(trim(services)) BETWEEN 1 AND 1000),
    email        TEXT NOT NULL DEFAULT '' CHECK(length(email) <= 254),
    phone        TEXT NOT NULL DEFAULT '' CHECK(length(phone) <= 30),
    address      TEXT NOT NULL DEFAULT '' CHECK(length(address) <= 300),
    createdDate  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status       TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Suspended')),
    revision     INTEGER NOT NULL DEFAULT 1
);

-- US41 - US45: IDP categories managed by the Platform Manager. Existing tables are retained.
CREATE TABLE IF NOT EXISTS idp_category (
    categoryId    INTEGER PRIMARY KEY AUTOINCREMENT,
    categoryName  TEXT NOT NULL UNIQUE COLLATE NOCASE,  -- 3-50 chars, capitals don't matter
    description   TEXT NOT NULL DEFAULT '' CHECK(length(description) <= 500),
    status        TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Suspended')),
    createdDate   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- US20: interior design projects (IDPs). designerId is the owner's userId.
CREATE TABLE IF NOT EXISTS idp (
    idpId        INTEGER PRIMARY KEY AUTOINCREMENT,
    designerId   INTEGER NOT NULL REFERENCES user_account(userId),
    categoryId   INTEGER NOT NULL REFERENCES idp_category(categoryId),
    title        TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 3 AND 100),
    description  TEXT NOT NULL CHECK(length(trim(description)) BETWEEN 1 AND 2000),
    location     TEXT NOT NULL DEFAULT '' CHECK(length(location) <= 200),
    projectType  TEXT NOT NULL DEFAULT 'Current' CHECK(projectType IN ('Current', 'Past')),
    status       TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Suspended')),
    createdDate  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- US33 - US35: Saved List / Favourites (Customer)
CREATE TABLE IF NOT EXISTS saved_idp (
    savedId      INTEGER PRIMARY KEY AUTOINCREMENT,
    customerId   INTEGER NOT NULL REFERENCES user_account(userId) ON DELETE CASCADE,
    idpId        INTEGER NOT NULL REFERENCES idp(idpId) ON DELETE CASCADE,
    savedDate    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customerId, idpId) -- Prevents duplicate saves
);



-- US37 and category popularity reporting: every public IDP detail page view.
CREATE TABLE IF NOT EXISTS idp_view (
    viewId INTEGER PRIMARY KEY AUTOINCREMENT,
    idpId INTEGER NOT NULL REFERENCES idp(idpId) ON DELETE CASCADE,
    viewedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_idp_view_project_date ON idp_view(idpId, viewedAt);
CREATE INDEX IF NOT EXISTS idx_saved_idp_project_date ON saved_idp(idpId, savedDate);
