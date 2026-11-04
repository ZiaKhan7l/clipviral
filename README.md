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
Apne GitHub repo (ZiaKhan7l/clipviral) mein jayein, "Add file" -> "Create new file" par click karein, file ka naam README.md rakhein, aur niche diya gaya poora code copy-paste kar ke Commit changes kar dein:
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

🚀 Getting Started
Prerequisites
 * Python 3.9 or higher
 * An OpenAI API Key
Local Installation
 * Clone the repository:
   git clone [https://github.com/ZiaKhan7l/clipviral.git](https://github.com/ZiaKhan7l/clipviral.git)
cd clipviral

 * Install dependencies:
   pip install -r requirements.txt

 * Set up your environment variables:
   export OPENAI_API_KEY="your-openai-api-key-here"

 * Run the application:
   python app.py

   Open your browser and navigate to http://localhost:5000 (or the port specified in your console).
☁️ Deploying to Railway
ClipViral is pre-configured for effortless hosting on Railway:
 * Fork or push this repository to your GitHub account.
 * Create a new project on Railway and select Deploy from GitHub repo.
 * Add your OPENAI_API_KEY in the Variables tab.
 * Railway will automatically detect railway.json and nixpacks.toml to build and deploy your live URL. (See DEPLOY_GUIDE.txt for detailed troubleshooting).
🛣️ Roadmap
 * [ ] Integration with OpenAI gpt-4o and o3-mini for faster timestamp reasoning.
 * [ ] Multi-language subtitle translation and burned-in caption styling.
 * [ ] Batch processing support for automated channel workflows.
 * [ ] Open-source prompt library for viral hook generation.
🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit a pull request.
📄 License
This project is open-source and available under the MIT License.
