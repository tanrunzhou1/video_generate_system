import wave
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import CharacterProfile, ShotDialogue, ShotPlan, SubtitleSegment, VoiceAsset

settings = get_settings()

VOICE_PROVIDER = "xtts-v2"
VOICE_SOURCE = "shot_dialogues"
SUBTITLE_SOURCE = "voice_assets"


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


def _estimate_duration(text: str) -> float:
    return max(round(len(text.strip()) * 0.18, 2), 0.8)


def generate_voice_assets_for_shot(
    db: Session,
    project_id: int,
    shot_id: int,
    provider: str,
    source: str,
) -> list[VoiceAsset]:
    if provider != VOICE_PROVIDER:
        raise ValueError("unsupported provider")
    if source != VOICE_SOURCE:
        raise ValueError("unsupported source")

    shot = db.get(ShotPlan, shot_id)
    if shot is None or shot.project_id != project_id:
        raise ValueError("shot not found")

    dialogues = (
        db.execute(
            select(ShotDialogue)
            .where(ShotDialogue.project_id == project_id, ShotDialogue.shot_id == shot_id)
            .order_by(ShotDialogue.sequence_no.asc(), ShotDialogue.id.asc())
        )
        .scalars()
        .all()
    )
    if not dialogues:
        raise ValueError("shot_dialogue not found")

    profile_by_name = {
        item.name: item
        for item in db.execute(
            select(CharacterProfile).where(CharacterProfile.project_id == project_id)
        ).scalars()
    }

    db.execute(delete(VoiceAsset).where(VoiceAsset.project_id == project_id, VoiceAsset.shot_id == shot_id))

    current_start = 0.0
    created_items: list[VoiceAsset] = []
    for dialogue in dialogues:
        character = profile_by_name.get(dialogue.character_name)
        if character is None:
            raise ValueError("character profile not found for dialogue")

        duration = _estimate_duration(dialogue.text)
        end_time = round(current_start + duration, 2)
        voice_asset = VoiceAsset(
            project_id=project_id,
            shot_id=shot_id,
            character_id=character.id,
            line_text=dialogue.text,
            voice_provider=provider,
            audio_path="",
            start_time_sec=current_start,
            end_time_sec=end_time,
        )
        db.add(voice_asset)
        db.flush()

        audio_path = (
            Path(settings.storage_dir)
            / "projects"
            / str(project_id)
            / "voice"
            / f"shot_{shot_id}_dialogue_{dialogue.id}.wav"
        )
        _write_silent_wav(audio_path, duration)
        voice_asset.audio_path = str(audio_path)
        setattr(voice_asset, "dialogue_id", dialogue.id)
        created_items.append(voice_asset)
        current_start = end_time

    db.commit()
    for item in created_items:
        db.refresh(item)
    return created_items


def list_voice_assets_for_shot(db: Session, project_id: int, shot_id: int) -> list[VoiceAsset]:
    items = (
        db.execute(
            select(VoiceAsset)
            .where(VoiceAsset.project_id == project_id, VoiceAsset.shot_id == shot_id)
            .order_by(VoiceAsset.start_time_sec.asc(), VoiceAsset.id.asc())
        )
        .scalars()
        .all()
    )
    dialogue_map = {
        (item.character_name, item.text): item.id
        for item in db.execute(
            select(ShotDialogue).where(ShotDialogue.project_id == project_id, ShotDialogue.shot_id == shot_id)
        ).scalars()
    }
    character_name_map = {
        item.id: item.name
        for item in db.execute(select(CharacterProfile).where(CharacterProfile.project_id == project_id)).scalars()
    }
    for item in items:
        setattr(item, "dialogue_id", dialogue_map.get((character_name_map.get(item.character_id, ""), item.line_text), 0))
    return items


def generate_subtitle_segments_for_shot(
    db: Session,
    project_id: int,
    shot_id: int,
    source: str,
) -> list[SubtitleSegment]:
    if source != SUBTITLE_SOURCE:
        raise ValueError("unsupported source")

    voice_assets = list_voice_assets_for_shot(db, project_id, shot_id)
    if not voice_assets:
        raise ValueError("voice_asset not found")

    db.execute(delete(SubtitleSegment).where(SubtitleSegment.project_id == project_id, SubtitleSegment.shot_id == shot_id))

    items: list[SubtitleSegment] = []
    for voice in voice_assets:
        segment = SubtitleSegment(
            project_id=project_id,
            shot_id=shot_id,
            text=voice.line_text,
            start_time_sec=voice.start_time_sec,
            end_time_sec=voice.end_time_sec,
        )
        db.add(segment)
        db.flush()
        items.append(segment)

    db.commit()
    for item in items:
        db.refresh(item)
    return items


def list_subtitle_segments_for_shot(db: Session, project_id: int, shot_id: int) -> list[SubtitleSegment]:
    return (
        db.execute(
            select(SubtitleSegment)
            .where(SubtitleSegment.project_id == project_id, SubtitleSegment.shot_id == shot_id)
            .order_by(SubtitleSegment.start_time_sec.asc(), SubtitleSegment.id.asc())
        )
        .scalars()
        .all()
    )
