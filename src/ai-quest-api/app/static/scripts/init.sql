START TRANSACTION;

CREATE DATABASE ai_quest;
USE ai_quest;
CREATE TABLE stories (
                         id BINARY(16) PRIMARY KEY,
                         user_id BINARY(16) NOT NULL
);

CREATE TABLE messages (
                          id BINARY(16) PRIMARY KEY,
                          role VARCHAR(50) NOT NULL,
                          content TEXT NOT NULL,
                          story_id BINARY(16),
                          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
);

COMMIT;
