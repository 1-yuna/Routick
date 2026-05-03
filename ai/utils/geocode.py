import os
import requests

# 카카오 REST API 키
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# 키워드 검색 API URL
KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

# 좌표로 바꿔주는 함수
def geocode_kakao(query: str, timeout: float = 3.0):

    # API 키 없으면 호출 불가
    if not KAKAO_REST_API_KEY:
        return None, "KAKAO_REST_API_KEY 미설정"

    try:
        # 카카오 키워드 검색 API 호출
        resp = requests.get(
            KAKAO_KEYWORD_URL,
            headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
            params={
                "query": query,  # 검색어
                "size": 1        # 결과 1개만 사용
            },
            timeout=timeout,
        )

        # HTTP 에러 체크 (200 아니면 예외 발생)
        resp.raise_for_status()

        # 응답 JSON에서 documents 추출
        docs = resp.json().get("documents", [])

        # 결과 없으면 실패 처리
        if not docs:
            return None, "검색 결과 없음"

        doc = docs[0]

        # Kakao API는 x=경도, y=위도
        latitude = float(doc["y"])
        longitude = float(doc["x"])

        return (latitude, longitude), None

    except requests.RequestException as e:
        # 네트워크 / API 요청 실패
        return None, f"Kakao API 호출 실패: {e}"

    except (KeyError, ValueError) as e:
        # 응답 구조 이상 or 타입 변환 실패
        return None, f"응답 파싱 실패: {e}"