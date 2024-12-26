from django.db import models

class Match(models.Model):
    class Meta:
        db_table = 'match'

    match_id = models.CharField(max_length=100, unique=True)  # Riot의 매치 ID
    game_mode = models.CharField(max_length=50, null=True, blank=True)  # 게임 모드 (예: 랭크, 일반)
    game_duration = models.IntegerField(null=True, blank=True)  # 게임 시간 (초)
    created_at = models.DateTimeField(auto_now_add=True)  # 매치 생성 시간

    def __str__(self):
        return f"Match {self.match_id} ({self.game_mode})"

class MatchParticipant(models.Model):
    class Meta:
        db_table = 'matchparticipant'

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="participants")  # Match와의 관계
    summoner_name = models.CharField(max_length=100)  # 소환사 이름
    summoner_id = models.CharField(max_length=100, null=True, blank=True)  # 소환사 ID
    champion_name = models.CharField(max_length=100)  # 사용한 챔피언 이름
    role = models.CharField(max_length=50, null=True, blank=True)  # 역할 (탑, 정글, 미드 등)
    kills = models.IntegerField(null=True, blank=True)
    deaths = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.summoner_name} ({self.role})"
