-- ============================================================
-- Image Library Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS imagelibrary;
USE imagelibrary;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL  -- store Werkzeug password hashes
);

-- Category table
CREATE TABLE IF NOT EXISTS category (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(200) NOT NULL,
    country VARCHAR(10)  NOT NULL DEFAULT 'UK',
    deleted TINYINT(1)   NOT NULL DEFAULT 0
);

-- Image library table
CREATE TABLE IF NOT EXISTS imagelibrary (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    category_id    INT          NOT NULL,
    image_name     VARCHAR(255) NOT NULL,
    file_path      VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500) NOT NULL,
    file_size      BIGINT       NOT NULL DEFAULT 0,
    country        VARCHAR(10)  NOT NULL DEFAULT 'UK',
    deleted        TINYINT(1)   NOT NULL DEFAULT 0,
    metadata       TEXT,
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_image_category FOREIGN KEY (category_id) REFERENCES category (id)
);

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_category_deleted     ON category     (deleted);
CREATE INDEX IF NOT EXISTS idx_image_deleted        ON imagelibrary (deleted);
CREATE INDEX IF NOT EXISTS idx_image_category_id    ON imagelibrary (category_id);
CREATE INDEX IF NOT EXISTS idx_image_created_at     ON imagelibrary (created_at);

-- ============================================================
-- Migration helpers for EXISTING databases
-- Run sections below only if upgrading an existing installation
-- ============================================================

-- ALTER TABLE category  ADD COLUMN IF NOT EXISTS country  VARCHAR(10)  NOT NULL DEFAULT 'UK';
-- ALTER TABLE category  ADD COLUMN IF NOT EXISTS deleted  TINYINT(1)   NOT NULL DEFAULT 0;
-- ALTER TABLE imagelibrary ADD COLUMN IF NOT EXISTS country VARCHAR(10) NOT NULL DEFAULT 'UK';
-- ALTER TABLE imagelibrary ADD COLUMN IF NOT EXISTS deleted TINYINT(1)  NOT NULL DEFAULT 0;
-- ALTER TABLE imagelibrary MODIFY COLUMN file_size BIGINT NOT NULL DEFAULT 0;