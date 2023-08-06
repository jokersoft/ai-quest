CREATE TABLE messages (
                          id BINARY(16) NOT NULL DEFAULT (UUID_TO_BIN(UUID())),
                          user_id BINARY(16) NOT NULL,
                          role VARCHAR(50),
                          content VARCHAR(1000),
                          type ENUM('situation', 'choice', 'decision', 'outcome', 'other'),
                          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
