from django.db import models

class User(models.Model):
    class Meta:
        db_table = 'user'

    id = models.AutoField(primary_key=True)
    unique_id = models.CharField(max_length=255, unique=True, db_index=True)
    account_id = models.CharField(max_length=255, db_index=True)
    puuid = models.CharField(max_length=255, db_index=True)
    profile_icon_id = models.IntegerField()
    revision_date = models.BigIntegerField()
    summoner_level = models.IntegerField()

    # 날짜/시간 필드
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 업데이트 시간

    def __str__(self):
        return f"User {self.unique_id} - Level {self.summoner_level}"
