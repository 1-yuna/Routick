INSERT INTO users (id, nickname, email, provider, created_at, updated_at)
VALUES (1, '테스트유저', 'test@routick.com', 'EMAIL', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;