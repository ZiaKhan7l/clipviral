import os
import json
import uuid
import time
import subprocess
import tempfile
import threading
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import yt_dlp
from groq import Groq

app = Flask(__name__, static_folder='static')
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
JOBS = {}  # job_id -> status dict
CLIPS_DIR = tempfile.mkdtemp()

# ─────────────────────────────────────────
#  SERVE FRONTEND
# ─────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ─────────────────────────────────────────
#  1. DETECT VIDEO INFO
# ─────────────────────────────────────────
@app.route("/api/detect", methods=["POST"])
def detect_video():
    data = request.json or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "forcejson": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        duration_sec = info.get("duration", 0)
        mins = duration_sec // 60
        secs = duration_sec % 60
        duration_str = f"{mins}:{secs:02d}"

        thumbnails = info.get("thumbnails", [])
        thumb = thumbnails[-1]["url"] if thumbnails else info.get("thumbnail", "")

        return jsonify({
            "title":    info.get("title", "Unknown"),
            "channel":  info.get("uploader", info.get("channel", "Unknown")),
            "duration": duration_str,
            "duration_sec": duration_sec,
            "thumbnail": thumb,
            "platform": info.get("extractor_key", "Unknown"),
            "view_count": info.get("view_count", 0),
            "like_count": info.get("like_count", 0),
            "upload_date": info.get("upload_date", ""),
            "description": (info.get("description", "") or "")[:300],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ─────────────────────────────────────────
#  2. START PROCESSING JOB
# ─────────────────────────────────────────
@app.route("/api/process", methods=["POST"])
def process_video():
    data = request.json or {}
    url      = data.get("url", "").strip()
    platform = data.get("platform", "tiktok")
    count    = int(data.get("count", 5))
    focus    = data.get("focus", "engagement")
    min_len  = int(data.get("min_len", 20))
    max_len  = int(data.get("max_len", 60))

    if not url:
        return jsonify({"error": "No URL"}), 400
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY not set in environment"}), 500

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "status": "queued",
        "step": 0,
        "step_name": "Queued",
        "progress": 0,
        "clips": [],
        "error": None,
    }

    thread = threading.Thread(
        target=run_pipeline,
        args=(job_id, url, platform, count, focus, min_len, max_len),
        daemon=True
    )
    thread.start()
    return jsonify({"job_id": job_id})

# ─────────────────────────────────────────
#  3. JOB STATUS POLLING
# ─────────────────────────────────────────
@app.route("/api/status/<job_id>")
def job_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)

# ─────────────────────────────────────────
#  4. DOWNLOAD CLIP
# ─────────────────────────────────────────
@app.route("/api/clip/<job_id>/<int:clip_index>")
def download_clip(job_id, clip_index):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "Not ready"}), 404
    clips = job.get("clips", [])
    if clip_index >= len(clips):
        return jsonify({"error": "Clip index out of range"}), 404
    clip_path = clips[clip_index].get("file")
    if not clip_path or not os.path.exists(clip_path):
        return jsonify({"error": "Clip file missing"}), 404
    return send_file(clip_path, mimetype="video/mp4",
                     as_attachment=True,
                     download_name=f"clip_{clip_index+1}_ClipViral.mp4")

# ─────────────────────────────────────────
#  PIPELINE
# ─────────────────────────────────────────
def update_job(job_id, **kwargs):
    if job_id in JOBS:
        JOBS[job_id].update(kwargs)

def run_pipeline(job_id, url, platform, count, focus, min_len, max_len):
    job_dir = os.path.join(CLIPS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    audio_path = os.path.join(job_dir, "audio.mp3")
    video_path = os.path.join(job_dir, "video.%(ext)s")

    try:
        # ── STEP 1: Download ──
        update_job(job_id, status="running", step=1,
                   step_name="Downloading video", progress=5)

        ydl_opts = {
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "outtmpl": os.path.join(job_dir, "video.%(ext)s"),
            "quiet": True,
            "merge_output_format": "mp4",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
            "keepvideo": True,
        }

        # Download audio for transcription
        audio_opts = {
            "format": "bestaudio/best",
            "outtmpl": audio_path.replace(".mp3", ".%(ext)s"),
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
        }

        # Download video
        video_opts = {
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best[height<=720]",
            "outtmpl": os.path.join(job_dir, "video.%(ext)s"),
            "quiet": True,
            "merge_output_format": "mp4",
        }

        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        update_job(job_id, progress=20)

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = os.path.join(job_dir, f"video.mp4")
            # find the actual downloaded file
            for f in os.listdir(job_dir):
                if f.startswith("video") and f.endswith(".mp4"):
                    video_file = os.path.join(job_dir, f)
                    break

        update_job(job_id, progress=35, step=2, step_name="Transcribing audio")

        # ── STEP 2: Transcribe with Groq Whisper ──
        actual_audio = None
        for f in os.listdir(job_dir):
            if f.startswith("audio") and (f.endswith(".mp3") or f.endswith(".m4a") or f.endswith(".webm")):
                actual_audio = os.path.join(job_dir, f)
                break

        if not actual_audio:
            raise Exception("Audio file not found after download")

        client = Groq(api_key=GROQ_API_KEY)
        with open(actual_audio, "rb") as af:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(actual_audio), af.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments = transcription.segments if hasattr(transcription, 'segments') else []
        full_text = transcription.text if hasattr(transcription, 'text') else ""

        update_job(job_id, progress=55, step=3, step_name="AI scoring moments")

        # ── STEP 3: AI Score with Groq LLaMA ──
        segments_for_ai = [
            {"id": i, "start": round(s.start, 1), "end": round(s.end, 1), "text": s.text}
            for i, s in enumerate(segments)
        ] if segments else []

        prompt = f"""You are a viral content expert. Analyze this video transcript and find the {count} best segments to make viral {platform} short clips.

TRANSCRIPT SEGMENTS:
{json.dumps(segments_for_ai[:80], indent=2)}

FOCUS: {focus}
MIN LENGTH: {min_len} seconds
MAX LENGTH: {max_len} seconds

Return ONLY valid JSON array. Each item must have:
- "start": start time in seconds (number)
- "end": end time in seconds (number)  
- "title": viral hook title (max 60 chars)
- "reason": why this is viral (max 100 chars)
- "score": virality score 1-100 (number)
- "captions": array of {{"time":"0:00","text":"..."}} (3-4 lines from the segment)
- "hashtags": array of 6 relevant hashtags

Make sure end - start is between {min_len} and {max_len} seconds.
Sort by score descending.
Return ONLY the JSON array, nothing else."""

        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )

        ai_text = chat.choices[0].message.content.strip()
        # Clean JSON
        if "```" in ai_text:
            ai_text = ai_text.split("```")[1]
            if ai_text.startswith("json"):
                ai_text = ai_text[4:]
        ai_text = ai_text.strip()

        try:
            clip_suggestions = json.loads(ai_text)
        except:
            # Fallback: auto-generate segments if AI parsing fails
            clip_suggestions = auto_segments(segments, count, min_len, max_len)

        clip_suggestions = clip_suggestions[:count]
        update_job(job_id, progress=70, step=4, step_name="Cutting clips with FFmpeg")

        # ── STEP 4: Cut clips with FFmpeg ──
        result_clips = []
        for idx, seg in enumerate(clip_suggestions):
            start = float(seg.get("start", 0))
            end   = float(seg.get("end", start + 30))
            duration = end - start
            if duration < 5:
                end = start + 30
                duration = 30

            out_path = os.path.join(job_dir, f"clip_{idx+1}.mp4")

            # FFmpeg: cut + scale to 9:16 (1080x1920) + add padding
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-i", video_file,
                "-t", str(duration),
                "-vf", (
                    "scale=1080:1920:force_original_aspect_ratio=decrease,"
                    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black"
                ),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",
                out_path
            ]

            proc = subprocess.run(ffmpeg_cmd, capture_output=True, timeout=300)

            if proc.returncode == 0 and os.path.exists(out_path):
                seg["file"] = out_path
                seg["duration_str"] = f"{int(duration//60)}:{int(duration%60):02d}"
                seg["clip_index"] = idx
                result_clips.append(seg)
            else:
                # Try simpler cut without resize
                simple_cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(start),
                    "-i", video_file,
                    "-t", str(duration),
                    "-c:v", "libx264", "-preset", "fast",
                    "-c:a", "aac",
                    out_path
                ]
                proc2 = subprocess.run(simple_cmd, capture_output=True, timeout=300)
                if proc2.returncode == 0:
                    seg["file"] = out_path
                    seg["duration_str"] = f"{int(duration//60)}:{int(duration%60):02d}"
                    seg["clip_index"] = idx
                    result_clips.append(seg)

            progress = 70 + int((idx + 1) / len(clip_suggestions) * 25)
            update_job(job_id, progress=progress)

        update_job(job_id,
                   status="done",
                   step=6,
                   step_name="Complete!",
                   progress=100,
                   clips=result_clips,
                   transcript_preview=full_text[:500])

    except Exception as e:
        update_job(job_id, status="error", error=str(e), progress=0)


def auto_segments(segments, count, min_len, max_len):
    """Fallback: auto pick segments if AI fails"""
    if not segments:
        return []
    result = []
    step = max(1, len(segments) // (count + 1))
    for i in range(0, len(segments) - step, step):
        s = segments[i]
        e = segments[min(i + 3, len(segments)-1)]
        dur = e.end - s.start
        if dur < min_len:
            continue
        if dur > max_len:
            e_time = s.start + max_len
        else:
            e_time = e.end
        result.append({
            "start": s.start, "end": e_time,
            "title": f"Highlight moment {len(result)+1}",
            "reason": "Auto-selected high-activity segment",
            "score": 80 - len(result)*5,
            "captions": [{"time": "0:00", "text": s.text[:80]}],
            "hashtags": ["#viral","#shorts","#trending","#fyp","#reels","#content"],
        })
        if len(result) >= count:
            break
    return result


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
