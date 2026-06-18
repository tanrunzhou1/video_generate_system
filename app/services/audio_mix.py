import wave
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import AudioMixAsset, BgmAsset, ShotPlan, VoiceAsset

settings = get_settings()


def _write_silent_wav(dst: Path, duration_sec: float) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16000
    frame_count = max(int(sample_rate * duration_sec), 1)
    silence = b"\x00\x00" * frame_count
    with wave.open(str(dst), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(silence)


def register_bgm_asset(
    db: Session,
    project_id: int,
    file_path: str,
    mood_tag: str | None,
    start_time_sec: float,
    end_time_sec: float,
    gain_db: float,
) -> BgmAsset:
    normalized_path = file_path.strip()
    if not normalized_path:
        raise ValueError("file_path cannot be blank")
    if end_time_sec <= start_time_sec:
        raise ValueError("end_time_sec must be greater than start_time_sec")

    asset = BgmAsset(
        project_id=project_id,
        file_path=normalized_path,
        mood_tag=mood_tag.strip() if mood_tag else None,
        start_time_sec=start_time_sec,
        end_time_sec=end_time_sec,
        gain_db=gain_db,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def list_bgm_assets(db: Session, project_id: int) -> list[BgmAsset]:
    return (
        db.execute(
            select(BgmAsset)
            .where(BgmAsset.project_id == project_id)
            .order_by(BgmAsset.start_time_sec.asc(), BgmAsset.id.asc())
        )
        .scalars()
        .all()
    )


def create_audio_mix_for_shot(
    db: Session,
    project_id: int,
    shot_id: int,
    bgm_asset_id: int,
    ducking_gain_db: float,
    fade_in_sec: float,
    fade_out_sec: float,
) -> tuple[AudioMixAsset, list[VoiceAsset]]:
    if fade_in_sec < 0 or fade_out_sec < 0:
        raise ValueError("fade parameters must be >= 0")

    shot = db.get(ShotPlan, shot_id)
    if shot is None or shot.project_id != project_id:
        raise ValueError("shot not found")

    bgm_asset = db.get(BgmAsset, bgm_asset_id)
    if bgm_asset is None or bgm_asset.project_id != project_id:
        raise ValueError("bgm asset not found")

    voice_assets = (
        db.execute(
            select(VoiceAsset)
            .where(VoiceAsset.project_id == project_id, VoiceAsset.shot_id == shot_id)
            .order_by(VoiceAsset.start_time_sec.asc(), VoiceAsset.id.asc())
        )
        .scalars()
        .all()
    )
    if not voice_assets:
        raise ValueError("voice_asset not found")

    for item in db.execute(
        select(AudioMixAsset).where(AudioMixAsset.project_id == project_id, AudioMixAsset.shot_id == shot_id)
    ).scalars():
        item.is_selected = False

    mix_asset = AudioMixAsset(
        project_id=project_id,
        shot_id=shot_id,
        bgm_asset_id=bgm_asset.id,
        mixed_audio_path="",
        ducking_gain_db=ducking_gain_db,
        fade_in_sec=fade_in_sec,
        fade_out_sec=fade_out_sec,
        is_selected=True,
    )
    db.add(mix_asset)
    db.flush()

    voice_duration = max(item.end_time_sec for item in voice_assets)
    bgm_duration = max(bgm_asset.end_time_sec - bgm_asset.start_time_sec, 0.1)
    mix_duration = round(max(voice_duration, min(bgm_duration, shot.duration_sec or bgm_duration)), 2)

    output_path = (
        Path(settings.storage_dir)
        / "projects"
        / str(project_id)
        / "audio_mix"
        / f"shot_{shot_id}_mix_{mix_asset.id}.wav"
    )
    _write_silent_wav(output_path, mix_duration)
    mix_asset.mixed_audio_path = str(output_path)

    db.commit()
    db.refresh(mix_asset)
    return mix_asset, voice_assets
