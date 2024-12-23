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


@router.get("/get-winning-rate")
def get_user_win_rate(
    user_id: int = Query(..., description="유저의 user_id를 입력하세요")
):
    # user_id로 유저 정보 찾기
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    # user의 unique_id를 이용해 승/패 정보 가져오기
    league_url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{user.unique_id}"
    headers = {"X-Riot-Token": RIOT_TEST_KEY}
    league_response = requests.get(league_url, headers=headers)

    if league_response.status_code != 200:
        raise HTTPException(status_code=league_response.status_code, detail="리그 정보 조회 실패")

    league_data = league_response.json()

    # RANKED_SOLO_5x5 데이터 필터링
    solo_rank_info = next((entry for entry in league_data if entry["queueType"] == "RANKED_SOLO_5x5"), None)
    if not solo_rank_info:
        raise HTTPException(status_code=404, detail="솔로 랭크 정보가 없습니다")
    # 승/패 데이터 가져오기
    wins = solo_rank_info["wins"]
    losses = solo_rank_info["losses"]

    # 승률 계산
    total_games = wins + losses
    win_rate = (wins / total_games * 100) if total_games > 0 else 0

    return {
        "status": 200,
        "message": "유저 승/패 정보 및 승률 반환",
        "data": {
            "tier": solo_rank_info["tier"],
            "rank": solo_rank_info["rank"],
            "league_point": solo_rank_info["leaguePoints"],
            "wins": wins,
            "losses": losses,
            "win_rate": f"{win_rate:.2f}%"  # 소수점 2자리로 표시
        }
    }

@router.get("/get-matches")
def get_recent_matches(
    user_id: int = Query(..., description="유저의 user_id를 입력하세요")
):
    # user_id로 유저 정보 찾기
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    # puuid 가져오기
    puuid = user.puuid
    print(puuid)

    # 최근 매치 데이터 가져오기
    match_url = f"{BASE_URL}/lol/matches/v5/matches/by-puuid/{puuid}/ids?start=0&count=20"
    headers = {"X-Riot-Token": RIOT_TEST_KEY}
    match_response = requests.get(match_url, headers=headers)

    if match_response.status_code != 200:
        raise HTTPException(status_code=match_response.status_code, detail="매치 데이터 조회 실패")

    match_ids = match_response.json()

    if not match_ids:
        raise HTTPException(status_code=404, detail="최근 매치가 없습니다")

    return {
        "status": 200,
        "message": "최근 매치 목록 반환",
        "data": match_ids
    }