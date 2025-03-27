-- Initial admin user (password: admin123)
INSERT INTO users (name, email, password) 
VALUES ('Admin User', 'admin@matrizrfm.com.br', '$2a$10$DxQrXTx7uaGYBGTKzGx9cOvIkJ2Y38c0dx0lRKZbVEMjNxOGJj.r2');

-- Initial demo user (password: demo123)
INSERT INTO users (name, email, password) 
VALUES ('Demo User', 'demo@matrizrfm.com.br', '$2a$10$UYW/y1fKWfM4P9IXD6JCzO9PSOHMSQlNyMY0u8QJGgOlxhRZ66xGC'); 