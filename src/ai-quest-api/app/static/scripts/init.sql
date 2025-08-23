START TRANSACTION;

CREATE DATABASE ai_quest;
USE ai_quest;
CREATE TABLE users (
    id BINARY(16) PRIMARY KEY,
    email VARCHAR(254) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_email ON users(email);

CREATE TABLE stories (
    id BINARY(16) PRIMARY KEY,
    title VARCHAR(256) DEFAULT NULL,
    user_id BINARY(16) NOT NULL
);

CREATE TABLE messages (
    id BINARY(16) PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    story_id BINARY(16) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tags JSON,
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
);

CREATE TABLE chapters (
    id BINARY(16) PRIMARY KEY,
    narration TEXT NOT NULL,
    situation TEXT NOT NULL,
    choices JSON NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL,
    summary TEXT,
    number INTEGER NOT NULL,
    story_id BINARY(16) NOT NULL,
    INDEX idx_story_id (story_id),
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
);

COMMIT;
