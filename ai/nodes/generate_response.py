# ─────────────────────────────────────────────────────────────────────
# generate_response
# ─────────────────────────────────────────────────────────────────────
# select_itinerary에서 선택된 최종 동선을
# Spring 백엔드 응답 형식으로 변환
#
# 흐름:
#   1. 선택된 동선 데이터 변환
#   2. travel_days 기반 day 구성
#   3. 각 장소별 데이터 매핑
#   4. 마지막 day 숙소 제거
# ─────────────────────────────────────────────────────────────────────

from utils.route.greedy_nn import STAY_MINUTES


# ─── [노드] 응답 생성 ───
def generate_response(state: dict) -> dict:
    selected_itinerary = state["selected_itinerary"]
    ui = state["user_input"]
    transport_kr = ui.get("transport_kr", "도보")
    travel_days = ui.get("travel_days", 1)
    warnings = []

    # 이동수단 한국어 → Spring 영어 변환
    transport_map = {
        "도보":   "walk",
        "자동차": "car",
    }
    transport = transport_map.get(transport_kr, "walk")

    days = []
    for day_data in selected_itinerary:
        day_number = day_data["day_number"]
        itinerary = day_data["itinerary"]

        # 마지막 day 숙소 제거
        if day_number == travel_days:
            itinerary = [
                item for item in itinerary
                if item["place"].get("bucket") != "lodging"
            ]

        places = []
        for item in itinerary:
            p = item["place"]
            bucket = p.get("bucket", "other")
            stay_minutes = STAY_MINUTES.get(bucket, 60)

            places.append({
                "placeOrder":           item["order"],
                "placeId":              p.get("id", ""),
                "name":                 p.get("name", ""),
                "address":              p.get("road_address_name", ""),
                "placeUrl":             p.get("place_url", ""),
                "lat":                  p.get("lat", 0.0),
                "lng":                  p.get("lng", 0.0),
                "bucket":               p.get("bucket", "other"),
                "description":          item.get("recommendation_reason", ""),
                "stayMinutes":          stay_minutes,
                "arriveTime":           item.get("arrive_at", ""),
                "transportToNext":      transport,
                "travelMinutesToNext":  item.get("travel_to_next_minutes", 0),
            })

        days.append({
            "dayNumber": day_number,
            "places": places,
        })

    response = {"days": days}

    return {
        "response": response,
        "warnings": warnings,
        "step": "done",
    }