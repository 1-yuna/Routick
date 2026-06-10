# ─────────────────────────────────────────────────────────────────────
# db
# ─────────────────────────────────────────────────────────────────────
# PostgreSQL 비동기 연결 + places 테이블 upsert 헬퍼
#
# 흐름:
#   1. 커넥션 풀 싱글톤 생성/반환
#   2. state.candidates(메모리) + PostgreSQL(영구) 둘 다에 저장
# ─────────────────────────────────────────────────────────────────────


import os
from typing import Optional

import asyncpg

_pool: Optional[asyncpg.Pool] = None


# ─── 커넥션 풀 (싱글톤 패턴) ───
async def get_pool() -> asyncpg.Pool:

    # 풀 크기 설정 ( 최소 1개 + 동시에 최대 10개 연결 허용)
    global _pool
    if _pool is None:
        new_pool = await asyncpg.create_pool(  # type: ignore[misc]
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", os.getlogin()),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "travel_planner"),
            min_size=1,
            max_size=10,
        )
        if new_pool is None:
            raise RuntimeError("Failed to create asyncpg pool")
        _pool = new_pool

    return _pool


# ─── 앱 종료 시 호출 ───
# LangGraph 서버를 종료할 때 풀을 깔끔히 닫고 싶다면 호출
async def close_pool() -> None:

    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


# ─── PostgreSQL 연결 ───
async def upsert_places(places: list[dict]) -> int:

    if not places:
        return 0

    # 풀에서 연결 가져옴 (없으면 생성)
    pool = await get_pool()

    # asyncpg의 executemany는 tuple 리스트를 받음
    # 각 tuple의 값들은 SQL의 $1, $2, ... 자리에 순서대로 들어감
    rows = [
        (
            p["id"],  # $1: place_id
            p["name"],  # $2: name
            p.get("category", ""),  # $3: category
            p.get("category_group_code", ""),  # $4: category_group_code
            p.get("phone", ""),  # $5: phone
            p.get("address_name", ""),  # $6: address_name
            p.get("road_address_name", ""),  # $7: road_address_name
            p["lat"],  # $8: lat
            p["lng"],  # $9: lng
            p.get("place_url", ""),  # $10: place_url
        )
        for p in places
    ]

    # 풀에서 연결 하나 빌려서 사용 → with 블록 끝나면 자동 반납
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO places (
                place_id, name, category, category_group_code,
                phone, address_name, road_address_name,
                lat, lng, place_url, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
            ON CONFLICT (place_id) DO UPDATE SET
                name                = EXCLUDED.name,
                category            = EXCLUDED.category,
                category_group_code = EXCLUDED.category_group_code,
                phone               = EXCLUDED.phone,
                address_name        = EXCLUDED.address_name,
                road_address_name   = EXCLUDED.road_address_name,
                lat                 = EXCLUDED.lat,
                lng                 = EXCLUDED.lng,
                place_url           = EXCLUDED.place_url,
                updated_at          = NOW()
            """,
            rows,
        )

    return len(rows)