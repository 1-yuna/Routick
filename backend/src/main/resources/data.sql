INSERT INTO users (id, nickname, email, provider, created_at, updated_at)
VALUES (1, '테스트유저', 'test@routick.com', 'EMAIL', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 더미 유저 삽입 후 시퀀스를 현재 최대 id에 맞춤 (id 충돌 방지)
SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users));