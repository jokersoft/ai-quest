CREATE TABLE actions (
    id BINARY(16) NOT NULL DEFAULT (UUID_TO_BIN(UUID())),
    message_id VARCHAR(50),
    text VARCHAR(256),
    PRIMARY KEY (id)
);
