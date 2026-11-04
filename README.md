# 🎬 ClipViral

**ClipViral** is an open-source, AI-powered short-form video clipping, transcription, and viral metadata optimization web application. Built for independent content creators and developers, it provides a lightweight, self-hosted workflow to turn long-form content into engaging, viral-ready shorts.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)
![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet)

---

## ✨ Key Features

- **🎙️ Automated Transcription:** High-accuracy audio-to-text processing powered by OpenAI Whisper.
- **🔥 Viral Moment Detection:** Semantic analysis using OpenAI GPT models to identify high-retention hooks and engaging segments in long videos.
- **📈 Metadata & Hook Generator:** Automatically generates SEO-optimized titles, description hooks, and viral tags for YouTube Shorts, TikTok, and Reels.
- **⚡ Lightweight Web Interface:** Clean, responsive frontend (`index.html`) paired with a fast Python backend (`app.py`).
- **☁️ One-Click Cloud Deployment:** Pre-configured with `railway.json`, `nixpacks.toml`, and `Procfile` for instant deployment on Railway or Heroku.

---

## 📂 Project Structure

```text
clipviral/
├── app.py              # Core Python backend & API routing
├── index.html          # Frontend user interface
├── requirements.txt    # Python dependencies
├── railway.json        # Railway cloud deployment configuration
├── nixpacks.toml       # Nixpacks build configuration
├── Procfile            # Process file for cloud hosting
└── DEPLOY_GUIDE.txt    # Step-by-step deployment instructions
