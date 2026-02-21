# Quick Start Guide

Get CoCo running in 5 minutes with just an Anthropic API key.

## Prerequisites

- Python 3.10 or higher
- An Anthropic API key ([get one here](https://console.anthropic.com/))

## Installation

### Option A: pip install (recommended)

```bash
git clone https://github.com/keef75/CoCo.git
cd CoCo
pip install -e .
```

### Option B: With all consciousness extensions

```bash
pip install -e ".[all]"
```

### Option C: Specific extensions only

```bash
pip install -e ".[web]"           # Web search (Tavily)
pip install -e ".[audio]"         # Voice/TTS (ElevenLabs)
pip install -e ".[google]"        # Google Workspace
pip install -e ".[twitter]"       # Twitter integration
pip install -e ".[web,google]"    # Combine as needed
```

## Configuration

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

That's it for minimal setup. Add more keys to unlock features:

| Key | Feature |
|-----|---------|
| `TAVILY_API_KEY` | Web search |
| `ELEVENLABS_API_KEY` | Voice/TTS |
| `FREEPIK_API_KEY` | Image generation |
| `FAL_API_KEY` | Video generation |
| Twitter keys | Twitter posting |
| Google OAuth | Docs, Sheets, Calendar |

## Running CoCo

```bash
# Any of these work:
python -m coco
coco              # If installed via pip
python coco/cli.py
```

## First Conversation

Once CoCo starts, try:

```
You: Hello, what can you do?
You: Search the web for the latest AI news
You: Read the file README.md
You: /help
```

## Key Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/recall <query>` | Search your facts memory |
| `/facts` | Browse stored facts |
| `/memory health` | Check memory system status |
| `/tweet <text>` | Post a tweet (requires Twitter setup) |
| `/image <prompt>` | Generate an image (requires Freepik key) |

## Next Steps

- [Full Architecture Guide](ARCHITECTURE.md)
- [Google OAuth Setup](GOOGLE_OAUTH_SETUP.md)
- [Twitter Setup](TWITTER_SETUP.md)
- [Docker Setup](DOCKER_SETUP.md) (optional PostgreSQL)
