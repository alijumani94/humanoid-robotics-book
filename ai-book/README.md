# Humanoid Robotics E-Book with AI Chatbot

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator, featuring an intelligent RAG-powered chatbot to assist with learning robotics concepts.

## 🤖 AI Chatbot Feature

An intelligent chatbot powered by Retrieval-Augmented Generation (RAG) that answers questions about the robotics textbook with strict grounding to prevent hallucination.

### Key Features:
- ✅ **Grounded Responses**: Only answers from book content
- ✅ **Text Selection Mode**: Ask questions about selected text
- ✅ **Source Attribution**: Shows chapter/section references
- ✅ **Chat History**: Persistent conversation tracking
- ✅ **Mobile Responsive**: Works on all devices

### Quick Start:
See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for complete setup instructions.

### Documentation:
- 📋 [Setup Guide](./SETUP_GUIDE.md) - Deployment instructions
- 📊 [Project Summary](./PROJECT_SUMMARY.md) - Architecture & features
- 📝 [Specification](./spec-kit/specs/001-rag-chatbot.md) - Full spec
- 📅 [Implementation Plan](./spec-kit/plans/001-rag-chatbot-plan.md) - Development phases
- ✅ [Task Breakdown](./spec-kit/tasks/001-rag-chatbot-tasks.md) - 65 detailed tasks

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
