from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv
from urllib import parse

from backend.users.models import User
import requests
import os


router = APIRouter(prefix="/summoner")

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
RIOT_TEST_KEY = os.getenv("RIOT_TEST_KEY")
GET_PUUID_URL = os.getenv("GET_PUUID_URL")

@router.get("/")
def get_my_summoner():
    url = f"{BASE_URL}/lol/summoner/v4/summoners/me"
    headers = {
        "X-Riot-Token": RIOT_TEST_KEY
    }

    # 요청 보내기
    response = requests.get(url, headers=headers)
    print(response.text)

    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="API 키가 만료되었거나 권한이 없습니다.")
    elif response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="소환사 정보를 가져올 수 없습니다."
        )

    return response.json()


@router.get("/get-user")
def get_user_tier(
    user: str = Query(..., description="소환사의 이름을 입력하세요"),
    tag: str = Query(..., description="소환사의 태그라인을 입력하세요")
):
    # 소환사 이름 URL 인코딩
    encoded_name = parse.quote(user)

    # puuid 가져오기 요청
    puuid_url = f"{GET_PUUID_URL}/{encoded_name}/{tag}"
    headers = {"X-Riot-Token": RIOT_TEST_KEY}
    puuid_response = requests.get(puuid_url, headers=headers)

    if puuid_response.status_code != 200:
        raise HTTPException(status_code=puuid_response.status_code, detail="puuid 조회 실패")

    puuid_data = puuid_response.json()
    puuid = puuid_data["puuid"]

    # 기존 유저 확인
    existing_user = User.objects.filter(puuid=puuid).first()
    if existing_user:
        return {
            "status": 200,
            "message": "기존 유저 정보 반환",
            "data": {
                "id": existing_user.id,
            }
        }

    # 티어 정보 가져오기
    tier_url = f"{BASE_URL}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    tier_response = requests.get(tier_url, headers=headers)

    if tier_response.status_code != 200:
        raise HTTPException(status_code=tier_response.status_code, detail="티어 정보 조회 실패")

    tier_data = tier_response.json()

    # 새 유저 저장
    new_user = User.objects.create(
        unique_id=tier_data["id"],
        account_id=tier_data["accountId"],
        puuid=tier_data["puuid"],
        profile_icon_id=tier_data["profileIconId"],
        revision_date=tier_data["revisionDate"],
        summoner_level=tier_data["summonerLevel"]
    )

    return {
        "status": 200,
        "message": "새 유저 정보 조회 및 저장 완료",
        "data": {
            "id": new_user.id,
        }
    }
