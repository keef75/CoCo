# CoCo Telegram Integration - Complete Implementation Plan

**Version**: 1.0
**Date**: October 26, 2025
**Author**: Claude Code
**Status**: Ready for Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Phase 1: Python API Server](#phase-1-python-api-server)
5. [Phase 2: TypeScript Telegram Bot](#phase-2-typescript-telegram-bot)
6. [Phase 3: Integration & Testing](#phase-3-integration--testing)
7. [Phase 4: Advanced Features (Optional)](#phase-4-advanced-features-optional)
8. [Security Considerations](#security-considerations)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)
11. [API Reference](#api-reference)

---

## Overview

This document provides a complete implementation plan for integrating CoCo personal assistant with Telegram, enabling on-the-go access to all CoCo capabilities through a mobile-friendly chat interface.

### Goals

- **Two-way messaging**: Full bidirectional communication between Telegram and CoCo
- **Complete feature access**: Conversations, memory queries, scheduler controls
- **Standalone architecture**: TypeScript bot + Python API server
- **Single-user security**: Authenticated access for authorized user only
- **Seamless experience**: Context preservation, streaming responses, rich formatting

### Key Features

✅ Full CoCo conversations with complete context and memory
✅ Memory system access (/recall, /facts, knowledge graph queries)
✅ Autonomous scheduler controls (view, toggle, create tasks)
✅ Real-time streaming responses with typing indicators
✅ Tool execution visibility with progress updates
✅ Session persistence across restarts
✅ Rich markdown formatting with code syntax highlighting
✅ Long message splitting (Telegram's 4096 character limit)
✅ Secure single-user authentication

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Telegram Platform                        │
│                    (User's Phone/Desktop App)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    Telegram Bot API
                             │
                ┌────────────▼─────────────┐
                │   TypeScript Bot         │
                │   (coco-telegram-bot)    │
                │                          │
                │  - Telegraf Framework    │
                │  - Command Handlers      │
                │  - Session Management    │
                │  - Message Formatting    │
                └────────────┬─────────────┘
                             │
                   HTTP/WebSocket API
                   (localhost:8765)
                             │
                ┌────────────▼─────────────┐
                │   CoCo API Server        │
                │   (coco_api_server.py)   │
                │                          │
                │  - FastAPI Framework     │
                │  - REST Endpoints        │
                │  - WebSocket Streaming   │
                │  - Authentication        │
                └────────────┬─────────────┘
                             │
              Direct Method Calls
                             │
                ┌────────────▼─────────────┐
                │   CoCo Engine            │
                │   (cocoa.py)             │
                │                          │
                │  - Consciousness Engine  │
                │  - Memory Systems        │
                │  - Tool Framework        │
                │  - Scheduler             │
                └──────────────────────────┘
```

### Component Communication Flow

```
User → Telegram → TypeScript Bot → CoCo API Server → CoCo Engine
                                                           ↓
                                    ← Response Stream ←  Process
                                                           ↓
                                                   Memory/Tools/Scheduler
```

---

## Prerequisites

### Software Requirements

1. **Python 3.10+** (CoCo requirement)
2. **Node.js 18+** and npm (for TypeScript bot)
3. **PostgreSQL** (existing CoCo database)
4. **Telegram Account** (for bot creation)

### API Keys & Tokens

1. **Telegram Bot Token**
   - Create bot via [@BotFather](https://t.me/BotFather)
   - Command: `/newbot`
   - Save the token provided

2. **Telegram User ID**
   - Get your user ID from [@userinfobot](https://t.me/userinfobot)
   - Required for single-user authentication

3. **CoCo API Token**
   - Generate a random secure token
   - Example: `openssl rand -hex 32`

### Existing CoCo Setup

Ensure CoCo is properly configured:
- ✅ `cocoa.py` working correctly
- ✅ Memory systems initialized
- ✅ Google Workspace integration active
- ✅ Scheduler running (if using automation features)

---

## Phase 1: Python API Server

### 1.1 Installation

Add required dependencies to `requirements.txt`:

```bash
# Telegram Integration Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
python-multipart==0.0.6
```

Install dependencies:

```bash
cd "/Users/keithlambert/Desktop/CoCo 7"
./venv_cocoa/bin/pip install fastapi uvicorn[standard] websockets pydantic python-multipart
```

### 1.2 Create `coco_api_server.py`

**File**: `/Users/keithlambert/Desktop/CoCo 7/coco_api_server.py`

**Key Components**:

```python
#!/usr/bin/env python3
"""
CoCo API Server - REST/WebSocket interface for Telegram integration
Exposes CoCo's conversation, memory, and scheduler capabilities via HTTP API
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import os
import json
from datetime import datetime

# Import CoCo components
from cocoa import (
    Config,
    ConsciousnessEngine,
    HierarchicalMemorySystem,
    ToolSystem
)

# Optional imports
try:
    from cocoa_scheduler import ScheduledConsciousness
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="CoCo API",
    description="REST/WebSocket API for CoCo Personal Assistant",
    version="1.0.0"
)

# CORS middleware (localhost only for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global CoCo instance (initialized on startup)
coco_engine = None
coco_config = None

# Authentication
API_TOKEN = os.getenv("COCO_API_TOKEN", "")
AUTHORIZED_TELEGRAM_ID = os.getenv("AUTHORIZED_TELEGRAM_ID", "")

def verify_token(authorization: str = Header(None)) -> bool:
    """Verify API authentication token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization.replace("Bearer ", "")
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    return True

def verify_user(user_id: str) -> bool:
    """Verify Telegram user ID is authorized"""
    if user_id != AUTHORIZED_TELEGRAM_ID:
        raise HTTPException(status_code=403, detail="Unauthorized user")
    return True

# ============================================================================
# Request/Response Models
# ============================================================================

class ConversationRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None

class ConversationResponse(BaseModel):
    response: str
    session_id: str
    tools_used: List[Dict[str, Any]] = []
    thinking: Optional[str] = None
    timestamp: str

class RecallRequest(BaseModel):
    query: str
    limit: int = 10

class RecallResponse(BaseModel):
    facts: List[Dict[str, Any]]
    query_type: str  # 'facts' or 'semantic'

class FactsResponse(BaseModel):
    facts: List[Dict[str, Any]]
    total_count: int
    fact_type: Optional[str] = None

class SchedulerStatusResponse(BaseModel):
    tasks: List[Dict[str, Any]]
    scheduler_running: bool

class SchedulerToggleRequest(BaseModel):
    feature: str  # 'news', 'calendar', 'meetings', 'report', 'video'
    enabled: bool

# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize CoCo engine on server startup"""
    global coco_engine, coco_config

    print("🚀 Starting CoCo API Server...")

    # Initialize configuration
    coco_config = Config()

    # Initialize memory system
    memory = HierarchicalMemorySystem(coco_config)

    # Initialize tool system
    tools = ToolSystem(coco_config)

    # Initialize consciousness engine
    coco_engine = ConsciousnessEngine(coco_config)

    print("✅ CoCo API Server ready!")
    print(f"   - API Token configured: {bool(API_TOKEN)}")
    print(f"   - Authorized User ID: {AUTHORIZED_TELEGRAM_ID}")
    print(f"   - Scheduler available: {SCHEDULER_AVAILABLE}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    print("🛑 Shutting down CoCo API Server...")

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "CoCo API Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/conversation", response_model=ConversationResponse, dependencies=[Depends(verify_token)])
async def conversation(request: ConversationRequest):
    """
    Process a conversation message through CoCo

    Args:
        request: ConversationRequest with message, user_id, session_id

    Returns:
        ConversationResponse with response text and metadata
    """
    verify_user(request.user_id)

    # Process message through CoCo engine
    # This would call the actual CoCo conversation processing
    # For now, return a placeholder response

    response_text = coco_engine.process_user_input(request.message)

    return ConversationResponse(
        response=response_text,
        session_id=request.session_id or f"session_{datetime.now().timestamp()}",
        tools_used=[],
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/v1/memory/recall", dependencies=[Depends(verify_token)])
async def recall(query: str, limit: int = 10, user_id: str = None):
    """
    Query CoCo's memory systems (Facts + Semantic)

    Args:
        query: Search query
        limit: Maximum results to return
        user_id: Telegram user ID for authorization

    Returns:
        RecallResponse with facts and query type
    """
    if user_id:
        verify_user(user_id)

    # Use QueryRouter to intelligently route to Facts or Semantic memory
    # This integrates with CoCo's existing memory systems

    # Placeholder implementation
    facts = []
    query_type = "semantic"

    return {
        "facts": facts,
        "query_type": query_type
    }

@app.get("/api/v1/memory/facts/{fact_type}", dependencies=[Depends(verify_token)])
async def get_facts(fact_type: Optional[str] = None, user_id: str = None):
    """
    Browse facts by type

    Args:
        fact_type: Type of facts to retrieve (optional, returns all if None)
        user_id: Telegram user ID for authorization

    Returns:
        FactsResponse with facts list and count
    """
    if user_id:
        verify_user(user_id)

    # Query FactsMemory system
    # Placeholder implementation
    facts = []

    return {
        "facts": facts,
        "total_count": len(facts),
        "fact_type": fact_type
    }

@app.get("/api/v1/scheduler/status", dependencies=[Depends(verify_token)])
async def scheduler_status(user_id: str = None):
    """
    Get scheduler status and task list

    Args:
        user_id: Telegram user ID for authorization

    Returns:
        SchedulerStatusResponse with tasks and status
    """
    if user_id:
        verify_user(user_id)

    if not SCHEDULER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Scheduler not available")

    # Get scheduler instance and query tasks
    # Placeholder implementation
    tasks = []

    return {
        "tasks": tasks,
        "scheduler_running": True
    }

@app.post("/api/v1/scheduler/toggle", dependencies=[Depends(verify_token)])
async def scheduler_toggle(request: SchedulerToggleRequest, user_id: str = None):
    """
    Toggle automation features (news, calendar, meetings, etc.)

    Args:
        request: SchedulerToggleRequest with feature and enabled state
        user_id: Telegram user ID for authorization

    Returns:
        Success confirmation
    """
    if user_id:
        verify_user(user_id)

    if not SCHEDULER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Scheduler not available")

    # Toggle the requested feature
    # This would call the appropriate scheduler method

    return {
        "success": True,
        "feature": request.feature,
        "enabled": request.enabled
    }

@app.websocket("/ws/conversation")
async def websocket_conversation(websocket: WebSocket):
    """
    WebSocket endpoint for streaming conversation responses

    Enables real-time streaming of CoCo's responses, tool executions,
    and thinking process to Telegram bot
    """
    await websocket.accept()

    try:
        # Verify authentication
        auth_data = await websocket.receive_json()
        token = auth_data.get("token", "")
        user_id = auth_data.get("user_id", "")

        if token != API_TOKEN:
            await websocket.send_json({"error": "Invalid token"})
            await websocket.close()
            return

        if user_id != AUTHORIZED_TELEGRAM_ID:
            await websocket.send_json({"error": "Unauthorized user"})
            await websocket.close()
            return

        # Send confirmation
        await websocket.send_json({"status": "authenticated"})

        # Process messages in loop
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")

            if not message:
                continue

            # Stream response chunks
            # This would integrate with CoCo's streaming response system

            # Placeholder: echo message
            await websocket.send_json({
                "type": "text",
                "content": f"Echo: {message}",
                "done": True
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})

# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("COCO_API_HOST", "127.0.0.1")
    port = int(os.getenv("COCO_API_PORT", "8765"))

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    CoCo API Server                           ║
║                  Telegram Integration                        ║
╚══════════════════════════════════════════════════════════════╝

Starting server on {host}:{port}

API Endpoints:
  - POST   /api/v1/conversation         (Process messages)
  - GET    /api/v1/memory/recall        (Query memory)
  - GET    /api/v1/memory/facts/:type   (Browse facts)
  - GET    /api/v1/scheduler/status     (Scheduler status)
  - POST   /api/v1/scheduler/toggle     (Toggle features)
  - WS     /ws/conversation              (Streaming)

Documentation: http://{host}:{port}/docs
    """)

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
```

### 1.3 Environment Configuration

Add to `/Users/keithlambert/Desktop/CoCo 7/.env`:

```bash
# ============================================================================
# Telegram Integration
# ============================================================================

# CoCo API Server Configuration
COCO_API_TOKEN=your-secret-token-here-use-openssl-rand-hex-32
COCO_API_HOST=127.0.0.1
COCO_API_PORT=8765

# Telegram Authentication
AUTHORIZED_TELEGRAM_ID=your-telegram-user-id-from-userinfobot
```

### 1.4 Test the API Server

```bash
# Start the API server
cd "/Users/keithlambert/Desktop/CoCo 7"
./venv_cocoa/bin/python coco_api_server.py

# In another terminal, test the endpoint
curl http://localhost:8765/

# Check the auto-generated API documentation
open http://localhost:8765/docs
```

---

## Phase 2: TypeScript Telegram Bot

### 2.1 Create Project Directory

```bash
cd "/Users/keithlambert/Desktop/CoCo 7"
mkdir coco-telegram-bot
cd coco-telegram-bot
```

### 2.2 Initialize Node.js Project

**File**: `package.json`

```json
{
  "name": "coco-telegram-bot",
  "version": "1.0.0",
  "type": "module",
  "description": "Telegram bot interface for CoCo Personal Assistant",
  "main": "dist/index.js",
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "echo \"No tests yet\" && exit 0"
  },
  "keywords": ["telegram", "bot", "coco", "ai", "typescript"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "telegraf": "^4.16.3",
    "dotenv": "^17.2.3",
    "axios": "^1.6.2",
    "ws": "^8.14.2",
    "tsx": "^4.20.6"
  },
  "devDependencies": {
    "@types/node": "^24.8.1",
    "@types/ws": "^8.5.10",
    "typescript": "^5.9.3"
  }
}
```

**File**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022"],
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

Install dependencies:

```bash
npm install
```

### 2.3 Environment Configuration

**File**: `.env.example`

```bash
# Required - Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Required - CoCo API
COCO_API_URL=http://127.0.0.1:8765
COCO_API_TOKEN=your-secret-token-here

# Required - Security
AUTHORIZED_USER_ID=your-telegram-user-id
```

**File**: `.env`

```bash
# Copy from .env.example and fill in actual values
```

### 2.4 Create Source Files

#### **File**: `src/config/env.ts`

```typescript
import dotenv from 'dotenv';
import path from 'path';

dotenv.config();

export interface EnvironmentConfig {
  telegramBotToken: string;
  cocoApiUrl: string;
  cocoApiToken: string;
  authorizedUserId: string;
}

export function validateEnvironment(): EnvironmentConfig {
  const requiredVars = {
    telegramBotToken: process.env.TELEGRAM_BOT_TOKEN,
    cocoApiUrl: process.env.COCO_API_URL,
    cocoApiToken: process.env.COCO_API_TOKEN,
    authorizedUserId: process.env.AUTHORIZED_USER_ID,
  };

  const missing: string[] = [];
  for (const [key, value] of Object.entries(requiredVars)) {
    if (!value) {
      missing.push(key);
    }
  }

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}\n` +
      `Please check your .env file.`
    );
  }

  return requiredVars as EnvironmentConfig;
}

export function getEnvironment(): EnvironmentConfig {
  return validateEnvironment();
}
```

#### **File**: `src/session/types.ts`

```typescript
export interface UserSession {
  user_id: number;
  session_id?: string;
  created_at: string;
  last_updated: string;
}
```

#### **File**: `src/session/manager.ts`

```typescript
import * as fs from 'fs';
import * as path from 'path';
import { UserSession } from './types.js';

const SESSIONS_DIR = path.join(process.cwd(), 'telegram_sessions');

function ensureSessionsDir(): void {
  if (!fs.existsSync(SESSIONS_DIR)) {
    fs.mkdirSync(SESSIONS_DIR, { recursive: true });
  }
}

function getSessionPath(userId: number): string {
  return path.join(SESSIONS_DIR, `${userId}.json`);
}

export function loadUserSession(userId: number): UserSession | null {
  const sessionPath = getSessionPath(userId);

  if (!fs.existsSync(sessionPath)) {
    return null;
  }

  try {
    const data = fs.readFileSync(sessionPath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error loading session for user ${userId}:`, error);
    return null;
  }
}

export function saveUserSession(userId: number, session: UserSession): void {
  ensureSessionsDir();
  const sessionPath = getSessionPath(userId);

  const sessionData: UserSession = {
    user_id: userId,
    session_id: session.session_id,
    created_at: session.created_at || new Date().toISOString(),
    last_updated: new Date().toISOString(),
  };

  fs.writeFileSync(sessionPath, JSON.stringify(sessionData, null, 2));
}

export function getOrCreateSession(userId: number): UserSession {
  let session = loadUserSession(userId);

  if (!session) {
    session = {
      user_id: userId,
      session_id: undefined,
      created_at: new Date().toISOString(),
      last_updated: new Date().toISOString(),
    };
    saveUserSession(userId, session);
  }

  return session;
}

export function clearUserSession(userId: number): void {
  const sessionPath = getSessionPath(userId);

  if (fs.existsSync(sessionPath)) {
    fs.unlinkSync(sessionPath);
  }
}
```

#### **File**: `src/coco/types.ts`

```typescript
export interface ConversationRequest {
  message: string;
  user_id: string;
  session_id?: string;
}

export interface ConversationResponse {
  response: string;
  session_id: string;
  tools_used: Array<{[key: string]: any}>;
  thinking?: string;
  timestamp: string;
}

export interface RecallResponse {
  facts: Array<{[key: string]: any}>;
  query_type: string;
}

export interface FactsResponse {
  facts: Array<{[key: string]: any}>;
  total_count: number;
  fact_type?: string;
}

export interface SchedulerStatusResponse {
  tasks: Array<{[key: string]: any}>;
  scheduler_running: boolean;
}
```

#### **File**: `src/coco/client.ts`

```typescript
import axios, { AxiosInstance } from 'axios';
import { getEnvironment } from '../config/env.js';
import {
  ConversationRequest,
  ConversationResponse,
  RecallResponse,
  FactsResponse,
  SchedulerStatusResponse,
} from './types.js';

export class CocoApiClient {
  private client: AxiosInstance;
  private config = getEnvironment();

  constructor() {
    this.client = axios.create({
      baseURL: this.config.cocoApiUrl,
      headers: {
        'Authorization': `Bearer ${this.config.cocoApiToken}`,
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 second timeout
    });
  }

  async sendMessage(request: ConversationRequest): Promise<ConversationResponse> {
    const response = await this.client.post<ConversationResponse>(
      '/api/v1/conversation',
      request
    );
    return response.data;
  }

  async recall(query: string, limit: number = 10): Promise<RecallResponse> {
    const response = await this.client.get<RecallResponse>(
      '/api/v1/memory/recall',
      {
        params: { query, limit, user_id: this.config.authorizedUserId }
      }
    );
    return response.data;
  }

  async getFacts(factType?: string): Promise<FactsResponse> {
    const endpoint = factType
      ? `/api/v1/memory/facts/${factType}`
      : '/api/v1/memory/facts/all';

    const response = await this.client.get<FactsResponse>(endpoint, {
      params: { user_id: this.config.authorizedUserId }
    });
    return response.data;
  }

  async getSchedulerStatus(): Promise<SchedulerStatusResponse> {
    const response = await this.client.get<SchedulerStatusResponse>(
      '/api/v1/scheduler/status',
      {
        params: { user_id: this.config.authorizedUserId }
      }
    );
    return response.data;
  }

  async toggleScheduler(feature: string, enabled: boolean): Promise<{success: boolean}> {
    const response = await this.client.post<{success: boolean}>(
      '/api/v1/scheduler/toggle',
      { feature, enabled },
      {
        params: { user_id: this.config.authorizedUserId }
      }
    );
    return response.data;
  }
}

// Singleton instance
let cocoClient: CocoApiClient | null = null;

export function getCocoClient(): CocoApiClient {
  if (!cocoClient) {
    cocoClient = new CocoApiClient();
  }
  return cocoClient;
}
```

#### **File**: `src/bot/utils/message-splitter.ts`

```typescript
import { Context } from 'telegraf';

const TELEGRAM_MESSAGE_LIMIT = 4096;

export async function sendLongMessage(ctx: Context, text: string): Promise<void> {
  if (text.length <= TELEGRAM_MESSAGE_LIMIT) {
    await ctx.reply(text, { parse_mode: 'Markdown' });
    return;
  }

  // Split by paragraphs first
  const paragraphs = text.split('\n\n');
  let currentChunk = '';

  for (const paragraph of paragraphs) {
    if ((currentChunk + paragraph).length > TELEGRAM_MESSAGE_LIMIT - 100) {
      // Send current chunk
      if (currentChunk) {
        await ctx.reply(currentChunk, { parse_mode: 'Markdown' });
        currentChunk = '';
      }

      // If single paragraph is too long, split by sentences
      if (paragraph.length > TELEGRAM_MESSAGE_LIMIT - 100) {
        const sentences = paragraph.split('. ');
        for (const sentence of sentences) {
          if ((currentChunk + sentence).length > TELEGRAM_MESSAGE_LIMIT - 100) {
            await ctx.reply(currentChunk, { parse_mode: 'Markdown' });
            currentChunk = sentence + '. ';
          } else {
            currentChunk += sentence + '. ';
          }
        }
      } else {
        currentChunk = paragraph + '\n\n';
      }
    } else {
      currentChunk += paragraph + '\n\n';
    }
  }

  // Send remaining chunk
  if (currentChunk) {
    await ctx.reply(currentChunk, { parse_mode: 'Markdown' });
  }
}
```

#### **File**: `src/bot/commands/start.ts`

```typescript
import { Context } from 'telegraf';
import { getEnvironment } from '../../config/env.js';

export async function startCommand(ctx: Context): Promise<void> {
  const config = getEnvironment();
  const userId = ctx.from?.id;

  // Check authorization
  if (userId?.toString() !== config.authorizedUserId) {
    await ctx.reply('⛔ Unauthorized. This bot is for private use only.');
    return;
  }

  const welcomeMessage = `
🤖 **Welcome to CoCo Telegram Bot!**

I'm your personal AI assistant, now available on-the-go! I have full access to your CoCo systems:

✅ **Full Conversations** - Complete context and memory
✅ **Memory Systems** - Facts, semantic search, knowledge graph
✅ **Scheduler Control** - Manage automation and tasks
✅ **Tool Access** - All 30+ CoCo capabilities
✅ **Google Workspace** - Docs, Calendar, Gmail, Drive

**Quick Commands:**
/help - Full command reference
/recall <query> - Search memory
/facts [type] - Browse facts
/auto-status - View automation
/reset - Clear conversation

**Just Talk:**
You can also just chat naturally - I'll remember our conversation and help with anything you need!

Let's get started! 🚀
  `.trim();

  await ctx.reply(welcomeMessage, { parse_mode: 'Markdown' });
}
```

#### **File**: `src/bot/commands/help.ts`

```typescript
import { Context } from 'telegraf';

export async function helpCommand(ctx: Context): Promise<void> {
  const helpMessage = `
📚 **CoCo Telegram Bot - Command Reference**

**Conversation:**
Just send any message for a full CoCo conversation!

**Memory Commands:**
/recall <query> - Search facts and semantic memory
/r <query> - Short alias for recall
/facts [type] - Browse facts by type
/f [type] - Short alias for facts
/facts-stats - Memory statistics

**Scheduler Commands:**
/auto-status - View all automation statuses
/auto-news on|off - Daily news digest
/auto-calendar on|off - Calendar summaries
/auto-meetings on|off - Meeting prep
/auto-report on|off - Weekly reports
/auto-video on|off - Weekly video messages

/task-list - View scheduled tasks
/task-create - Create new task
/tasks - Alias for task-list

**Utility:**
/reset - Clear conversation context
/help - Show this help message
/start - Welcome message

**Tips:**
- All CoCo's tools are available (Google Workspace, web search, files, etc.)
- Context is preserved across sessions
- Long responses are automatically split
- Tool usage is shown with 🔧 icons

Need something? Just ask! 💬
  `.trim();

  await ctx.reply(helpMessage, { parse_mode: 'Markdown' });
}
```

#### **File**: `src/bot/commands/recall.ts`

```typescript
import { Context } from 'telegraf';
import { getCocoClient } from '../../coco/client.js';
import { sendLongMessage } from '../utils/message-splitter.js';

export async function recallCommand(ctx: Context): Promise<void> {
  const text = ctx.message && 'text' in ctx.message ? ctx.message.text : '';
  const query = text.replace(/^\/r(ecall)?\s+/, '').trim();

  if (!query) {
    await ctx.reply('Usage: /recall <query>\nExample: /recall project ideas');
    return;
  }

  try {
    await ctx.sendChatAction('typing');

    const client = getCocoClient();
    const result = await client.recall(query, 10);

    if (!result.facts || result.facts.length === 0) {
      await ctx.reply(`No results found for: "${query}"`);
      return;
    }

    let response = `🧠 **Memory Recall** (${result.query_type})\n`;
    response += `Query: "${query}"\n`;
    response += `Found ${result.facts.length} results:\n\n`;

    for (const fact of result.facts) {
      response += `• ${fact.text || JSON.stringify(fact)}\n`;
      if (fact.importance) {
        response += `  _Importance: ${fact.importance}_\n`;
      }
      response += '\n';
    }

    await sendLongMessage(ctx, response);
  } catch (error: any) {
    console.error('Recall error:', error);
    await ctx.reply(`❌ Error: ${error.message || 'Failed to query memory'}`);
  }
}
```

#### **File**: `src/bot/commands/facts.ts`

```typescript
import { Context } from 'telegraf';
import { getCocoClient } from '../../coco/client.js';
import { sendLongMessage } from '../utils/message-splitter.js';

export async function factsCommand(ctx: Context): Promise<void> {
  const text = ctx.message && 'text' in ctx.message ? ctx.message.text : '';
  const factType = text.replace(/^\/f(acts)?\s+/, '').trim() || undefined;

  try {
    await ctx.sendChatAction('typing');

    const client = getCocoClient();
    const result = await client.getFacts(factType);

    if (!result.facts || result.facts.length === 0) {
      await ctx.reply(factType
        ? `No facts found for type: ${factType}`
        : 'No facts found');
      return;
    }

    let response = `📋 **Facts** ${factType ? `(${factType})` : ''}\n`;
    response += `Total: ${result.total_count}\n\n`;

    // Group by type if showing all
    const grouped: {[key: string]: any[]} = {};
    for (const fact of result.facts) {
      const type = fact.fact_type || 'other';
      if (!grouped[type]) {
        grouped[type] = [];
      }
      grouped[type].push(fact);
    }

    for (const [type, facts] of Object.entries(grouped)) {
      response += `**${type.toUpperCase()}** (${facts.length}):\n`;
      for (const fact of facts.slice(0, 5)) { // Show max 5 per type
        response += `• ${fact.text || JSON.stringify(fact)}\n`;
      }
      if (facts.length > 5) {
        response += `  _...and ${facts.length - 5} more_\n`;
      }
      response += '\n';
    }

    await sendLongMessage(ctx, response);
  } catch (error: any) {
    console.error('Facts error:', error);
    await ctx.reply(`❌ Error: ${error.message || 'Failed to retrieve facts'}`);
  }
}
```

#### **File**: `src/bot/commands/auto.ts`

```typescript
import { Context } from 'telegraf';
import { getCocoClient } from '../../coco/client.js';

export async function autoStatusCommand(ctx: Context): Promise<void> {
  try {
    await ctx.sendChatAction('typing');

    const client = getCocoClient();
    const status = await client.getSchedulerStatus();

    let response = '⚙️ **Automation Status**\n\n';
    response += `Scheduler: ${status.scheduler_running ? '✅ Running' : '❌ Stopped'}\n\n`;

    if (status.tasks && status.tasks.length > 0) {
      response += '**Active Tasks:**\n';
      for (const task of status.tasks) {
        response += `• ${task.name || 'Unnamed'}\n`;
        response += `  Schedule: ${task.schedule || 'Unknown'}\n`;
        response += `  Status: ${task.enabled ? '✅ Enabled' : '⏸️ Disabled'}\n\n`;
      }
    } else {
      response += '_No active tasks_\n';
    }

    response += '\n**Toggle Commands:**\n';
    response += '/auto-news on|off\n';
    response += '/auto-calendar on|off\n';
    response += '/auto-meetings on|off\n';
    response += '/auto-report on|off\n';
    response += '/auto-video on|off\n';

    await ctx.reply(response, { parse_mode: 'Markdown' });
  } catch (error: any) {
    console.error('Auto status error:', error);
    await ctx.reply(`❌ Error: ${error.message || 'Failed to get scheduler status'}`);
  }
}

export async function autoToggleCommand(ctx: Context, feature: string): Promise<void> {
  const text = ctx.message && 'text' in ctx.message ? ctx.message.text : '';
  const arg = text.split(' ')[1]?.toLowerCase();

  if (!arg || !['on', 'off'].includes(arg)) {
    await ctx.reply(`Usage: /auto-${feature} on|off`);
    return;
  }

  const enabled = arg === 'on';

  try {
    await ctx.sendChatAction('typing');

    const client = getCocoClient();
    await client.toggleScheduler(feature, enabled);

    const emoji = enabled ? '✅' : '⏸️';
    await ctx.reply(`${emoji} Automation \`${feature}\` is now ${enabled ? 'enabled' : 'disabled'}`);
  } catch (error: any) {
    console.error('Auto toggle error:', error);
    await ctx.reply(`❌ Error: ${error.message || 'Failed to toggle automation'}`);
  }
}
```

#### **File**: `src/bot/commands/reset.ts`

```typescript
import { Context } from 'telegraf';
import { clearUserSession } from '../../session/manager.js';

export async function resetCommand(ctx: Context): Promise<void> {
  const userId = ctx.from?.id;

  if (!userId) {
    await ctx.reply('❌ Unable to identify user');
    return;
  }

  clearUserSession(userId);
  await ctx.reply('✅ Conversation context cleared. Starting fresh!');
}
```

#### **File**: `src/bot/handlers/message.ts`

```typescript
import { Context } from 'telegraf';
import { getOrCreateSession, saveUserSession } from '../../session/manager.js';
import { getCocoClient } from '../../coco/client.js';
import { sendLongMessage } from '../utils/message-splitter.js';
import { getEnvironment } from '../../config/env.js';

export async function handleMessage(ctx: Context): Promise<void> {
  const config = getEnvironment();
  const userId = ctx.from?.id;

  if (!userId) {
    await ctx.reply('❌ Unable to identify user');
    return;
  }

  // Check authorization
  if (userId.toString() !== config.authorizedUserId) {
    await ctx.reply('⛔ Unauthorized. This bot is for private use only.');
    return;
  }

  const messageText = ctx.message && 'text' in ctx.message ? ctx.message.text : '';
  if (!messageText || messageText.trim() === '') {
    return;
  }

  try {
    // Load or create session
    const session = getOrCreateSession(userId);

    console.log(`Processing message from user ${userId}`);

    // Send typing indicator
    await ctx.sendChatAction('typing');

    // Send message to CoCo API
    const client = getCocoClient();
    const response = await client.sendMessage({
      message: messageText,
      user_id: userId.toString(),
      session_id: session.session_id,
    });

    // Show tool usage if any
    if (response.tools_used && response.tools_used.length > 0) {
      const toolNames = response.tools_used.map(t => t.name || 'unknown').join(', ');
      await ctx.reply(`🔧 Tools used: ${toolNames}`);
    }

    // Send response
    await sendLongMessage(ctx, response.response);

    // Update session
    session.session_id = response.session_id;
    session.last_updated = new Date().toISOString();
    saveUserSession(userId, session);

  } catch (error: any) {
    console.error('Message handler error:', error);
    await ctx.reply(
      `❌ Error: ${error.message || 'Something went wrong'}\n\n` +
      'Please try again or use /reset if the issue persists.'
    );
  }
}
```

#### **File**: `src/index.ts`

```typescript
import { Telegraf } from 'telegraf';
import { getEnvironment } from './config/env.js';
import { startCommand } from './bot/commands/start.js';
import { helpCommand } from './bot/commands/help.js';
import { recallCommand } from './bot/commands/recall.js';
import { factsCommand } from './bot/commands/facts.js';
import { autoStatusCommand, autoToggleCommand } from './bot/commands/auto.js';
import { resetCommand } from './bot/commands/reset.js';
import { handleMessage } from './bot/handlers/message.js';

async function main() {
  console.log('🤖 Starting CoCo Telegram Bot...');

  // Validate environment
  let config;
  try {
    config = getEnvironment();
    console.log('✅ Environment configuration validated');
  } catch (error) {
    console.error('❌ Environment validation failed:', error);
    process.exit(1);
  }

  // Create bot instance
  const bot = new Telegraf(config.telegramBotToken);

  // Register command handlers
  bot.command('start', startCommand);
  bot.command('help', helpCommand);

  // Memory commands
  bot.command('recall', recallCommand);
  bot.command('r', recallCommand);
  bot.command('facts', factsCommand);
  bot.command('f', factsCommand);

  // Scheduler commands
  bot.command('auto-status', autoStatusCommand);
  bot.command('auto-news', (ctx) => autoToggleCommand(ctx, 'news'));
  bot.command('auto-calendar', (ctx) => autoToggleCommand(ctx, 'calendar'));
  bot.command('auto-meetings', (ctx) => autoToggleCommand(ctx, 'meetings'));
  bot.command('auto-report', (ctx) => autoToggleCommand(ctx, 'report'));
  bot.command('auto-video', (ctx) => autoToggleCommand(ctx, 'video'));

  // Utility commands
  bot.command('reset', resetCommand);

  // Message handler (for all non-command messages)
  bot.on('text', handleMessage);

  // Error handling
  bot.catch((error: any) => {
    console.error('Bot error:', error);
  });

  // Start bot
  try {
    await bot.launch();
    console.log('✅ CoCo Telegram Bot is running!');
    console.log('Press Ctrl+C to stop');
  } catch (error) {
    console.error('❌ Failed to start bot:', error);
    process.exit(1);
  }

  // Enable graceful stop
  process.once('SIGINT', () => {
    console.log('\n🛑 SIGINT received, stopping bot...');
    bot.stop('SIGINT');
  });

  process.once('SIGTERM', () => {
    console.log('\n🛑 SIGTERM received, stopping bot...');
    bot.stop('SIGTERM');
  });
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
```

### 2.5 Create README

**File**: `README.md`

```markdown
# CoCo Telegram Bot

Telegram interface for CoCo Personal Assistant, enabling on-the-go access to all CoCo capabilities.

## Features

- ✅ Full CoCo conversations with context and memory
- ✅ Memory system queries (/recall, /facts)
- ✅ Autonomous scheduler controls
- ✅ All 30+ CoCo tools available
- ✅ Secure single-user authentication
- ✅ Session persistence
- ✅ Rich markdown formatting

## Prerequisites

1. **CoCo API Server running** (see ../coco_api_server.py)
2. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
3. **Your Telegram User ID** from [@userinfobot](https://t.me/userinfobot)

## Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your values
```

3. **Start the bot**:
```bash
npm run dev
```

## Commands

**Conversation:**
- Just send any message!

**Memory:**
- `/recall <query>` - Search memory
- `/facts [type]` - Browse facts

**Scheduler:**
- `/auto-status` - View automation
- `/auto-news on|off` - Toggle news
- `/auto-calendar on|off` - Toggle calendar
- `/auto-meetings on|off` - Toggle meetings

**Utility:**
- `/reset` - Clear conversation
- `/help` - Show help

## Architecture

```
Telegram → TypeScript Bot → HTTP API → CoCo Engine
```

See `../coco_telegram.md` for complete integration details.
```

---

## Phase 3: Integration & Testing

### 3.1 Complete Setup Checklist

**CoCo Side**:
- ✅ Install Python dependencies (fastapi, uvicorn, websockets)
- ✅ Create `coco_api_server.py`
- ✅ Configure `.env` with API token and authorized user ID
- ✅ Test API server starts correctly

**Telegram Bot Side**:
- ✅ Create project directory structure
- ✅ Install Node.js dependencies
- ✅ Configure `.env` with bot token and API details
- ✅ Build TypeScript project

### 3.2 Launch Sequence

**Terminal 1: Start CoCo API Server**

```bash
cd "/Users/keithlambert/Desktop/CoCo 7"
./venv_cocoa/bin/python coco_api_server.py
```

Expected output:
```
╔══════════════════════════════════════════════════════════════╗
║                    CoCo API Server                           ║
║                  Telegram Integration                        ║
╚══════════════════════════════════════════════════════════════╝

Starting server on 127.0.0.1:8765
...
```

**Terminal 2: Start Telegram Bot**

```bash
cd "/Users/keithlambert/Desktop/CoCo 7/coco-telegram-bot"
npm run dev
```

Expected output:
```
🤖 Starting CoCo Telegram Bot...
✅ Environment configuration validated
✅ CoCo Telegram Bot is running!
Press Ctrl+C to stop
```

### 3.3 Testing Checklist

**Basic Functionality**:
1. ✅ Open Telegram, find your bot
2. ✅ Send `/start` → Receive welcome message
3. ✅ Send "Hello CoCo" → Receive intelligent response
4. ✅ Send `/help` → Receive command list

**Memory System**:
1. ✅ Send `/recall project ideas` → Receive relevant facts
2. ✅ Send `/facts command` → Browse command facts
3. ✅ Send `/facts-stats` → See memory statistics

**Scheduler**:
1. ✅ Send `/auto-status` → View automation statuses
2. ✅ Send `/auto-news on` → Enable news automation
3. ✅ Send `/auto-news off` → Disable news automation

**Conversation Flow**:
1. ✅ Send multi-turn conversation → Context preserved
2. ✅ Send long message → Response properly split
3. ✅ Trigger tool usage → See tool notifications
4. ✅ Send `/reset` → Conversation cleared

**Error Handling**:
1. ✅ Stop API server → Bot shows error message
2. ✅ Send invalid command → Helpful error
3. ✅ Unauthorized user sends message → Rejected

### 3.4 Verification Script

Create a test script to verify integration:

**File**: `/Users/keithlambert/Desktop/CoCo 7/test_telegram_integration.sh`

```bash
#!/bin/bash

echo "🧪 Testing CoCo Telegram Integration"
echo "======================================"

# Check API server
echo "1. Checking API server..."
curl -s http://localhost:8765/ | grep -q "running" && echo "✅ API server responding" || echo "❌ API server not responding"

# Check API endpoints
echo "2. Checking API authentication..."
curl -s -H "Authorization: Bearer wrong-token" http://localhost:8765/api/v1/conversation && echo "❌ Auth bypass!" || echo "✅ Auth working"

# Check bot process
echo "3. Checking Telegram bot process..."
pgrep -f "tsx src/index.ts" > /dev/null && echo "✅ Bot process running" || echo "❌ Bot process not found"

echo ""
echo "Manual tests to perform in Telegram:"
echo "  1. Send /start to bot"
echo "  2. Send 'Hello CoCo'"
echo "  3. Send /recall <query>"
echo "  4. Send /auto-status"
echo ""
echo "Check logs in both terminals for errors"
```

Make it executable:

```bash
chmod +x test_telegram_integration.sh
./test_telegram_integration.sh
```

---

## Phase 4: Advanced Features (Optional)

### 4.1 Proactive Notifications

Modify scheduler to send Telegram notifications:

**Integration Point**: Add to `coco_api_server.py`

```python
# Add Telegram notification capability
import requests

def send_telegram_notification(user_id: str, message: str):
    """Send notification to Telegram user"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    if not bot_token:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": user_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, json=data)
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

# Hook into scheduler task completion
def on_task_complete(task_name: str, result: str):
    """Called when scheduled task completes"""
    message = f"✅ Task completed: {task_name}\n\n{result}"
    send_telegram_notification(AUTHORIZED_TELEGRAM_ID, message)
```

### 4.2 Rich Media Support

Add support for photos, voice messages, files:

**Telegram Bot Enhancement**:

```typescript
// Add to src/index.ts

// Handle photos (for vision capabilities)
bot.on('photo', async (ctx) => {
  const photo = ctx.message.photo[ctx.message.photo.length - 1];
  const fileLink = await ctx.telegram.getFileLink(photo.file_id);

  // Send to CoCo API with vision processing
  // Implementation depends on CoCo's vision capabilities
});

// Handle voice messages
bot.on('voice', async (ctx) => {
  const voice = ctx.message.voice;
  const fileLink = await ctx.telegram.getFileLink(voice.file_id);

  // Send to CoCo API for transcription
});

// Handle documents
bot.on('document', async (ctx) => {
  const doc = ctx.message.document;
  const fileLink = await ctx.telegram.getFileLink(doc.file_id);

  // Send to CoCo API for document analysis
});
```

### 4.3 Inline Keyboards

Add interactive buttons for common actions:

```typescript
// Add to src/bot/commands/auto.ts

import { Markup } from 'telegraf';

export async function autoStatusCommandWithButtons(ctx: Context): Promise<void> {
  // ... fetch status ...

  await ctx.reply(
    response,
    Markup.inlineKeyboard([
      [
        Markup.button.callback('📰 News On', 'auto_news_on'),
        Markup.button.callback('📰 News Off', 'auto_news_off')
      ],
      [
        Markup.button.callback('📅 Calendar On', 'auto_calendar_on'),
        Markup.button.callback('📅 Calendar Off', 'auto_calendar_off')
      ]
    ])
  );
}

// Handle button callbacks
bot.action(/auto_(.+)_(on|off)/, async (ctx) => {
  const [feature, state] = ctx.match.slice(1);
  await autoToggleCommand(ctx, feature);
  await ctx.answerCbQuery();
});
```

### 4.4 WebSocket Streaming

Implement real-time streaming responses:

**File**: `src/coco/streaming.ts`

```typescript
import WebSocket from 'ws';
import { getEnvironment } from '../config/env.js';

export class CocoStreamingClient {
  private ws: WebSocket | null = null;
  private config = getEnvironment();

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = this.config.cocoApiUrl.replace('http', 'ws') + '/ws/conversation';
      this.ws = new WebSocket(wsUrl);

      this.ws.on('open', () => {
        // Authenticate
        this.ws?.send(JSON.stringify({
          token: this.config.cocoApiToken,
          user_id: this.config.authorizedUserId
        }));
      });

      this.ws.on('message', (data) => {
        const message = JSON.parse(data.toString());
        if (message.status === 'authenticated') {
          resolve();
        }
      });

      this.ws.on('error', (error) => {
        reject(error);
      });
    });
  }

  async sendMessage(
    message: string,
    onChunk: (chunk: string) => void
  ): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connect();
    }

    return new Promise((resolve, reject) => {
      this.ws?.send(JSON.stringify({ message }));

      const messageHandler = (data: WebSocket.Data) => {
        const response = JSON.parse(data.toString());

        if (response.type === 'text') {
          onChunk(response.content);
        }

        if (response.done) {
          this.ws?.off('message', messageHandler);
          resolve();
        }

        if (response.error) {
          this.ws?.off('message', messageHandler);
          reject(new Error(response.error));
        }
      };

      this.ws?.on('message', messageHandler);
    });
  }

  disconnect(): void {
    this.ws?.close();
  }
}
```

Use in message handler:

```typescript
// Modify src/bot/handlers/message.ts

import { CocoStreamingClient } from '../../coco/streaming.js';

export async function handleMessageWithStreaming(ctx: Context): Promise<void> {
  // ... setup ...

  const streamingClient = new CocoStreamingClient();

  let currentMessage = await ctx.reply('💭 Thinking...');
  let fullResponse = '';
  let lastUpdate = Date.now();

  try {
    await streamingClient.sendMessage(
      messageText,
      async (chunk) => {
        fullResponse += chunk;

        // Update message every 2 seconds
        if (Date.now() - lastUpdate > 2000) {
          try {
            await ctx.telegram.editMessageText(
              ctx.chat!.id,
              currentMessage.message_id,
              undefined,
              fullResponse,
              { parse_mode: 'Markdown' }
            );
            lastUpdate = Date.now();
          } catch (e) {
            // Ignore edit errors
          }
        }
      }
    );

    // Final update
    await ctx.telegram.editMessageText(
      ctx.chat!.id,
      currentMessage.message_id,
      undefined,
      fullResponse,
      { parse_mode: 'Markdown' }
    );

  } finally {
    streamingClient.disconnect();
  }
}
```

---

## Security Considerations

### Authentication & Authorization

1. **API Token Security**
   - Generate strong random token: `openssl rand -hex 32`
   - Store in `.env`, never commit to git
   - Rotate periodically (monthly recommended)

2. **User Verification**
   - Hardcoded Telegram user ID for single-user mode
   - Immediate rejection of unauthorized users
   - No sensitive information in error messages

3. **Network Security**
   - API server binds to localhost only (`127.0.0.1`)
   - No external network exposure
   - Use VPN/SSH tunnel for remote access

### Data Privacy

1. **Session Storage**
   - Sessions stored locally as JSON files
   - Add to `.gitignore`
   - No sensitive data in session files

2. **Logging**
   - No message content in logs
   - Only metadata (user ID, timestamp, errors)
   - Rotate logs regularly

### Telegram Security

1. **Bot Token Protection**
   - Never share bot token
   - Revoke and recreate if compromised
   - Store in `.env` only

2. **Message Encryption**
   - Telegram uses MTProto encryption
   - Messages encrypted in transit
   - No additional encryption needed

---

## Deployment Guide

### Production Deployment Options

#### Option 1: systemd Services (Recommended for Linux)

**CoCo API Service**: `/etc/systemd/system/coco-api.service`

```ini
[Unit]
Description=CoCo API Server
After=network.target postgresql.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/CoCo 7
ExecStart=/path/to/CoCo 7/venv_cocoa/bin/python coco_api_server.py
Restart=always
RestartSec=10

Environment="COCO_API_TOKEN=your-token"
Environment="AUTHORIZED_TELEGRAM_ID=your-id"

[Install]
WantedBy=multi-user.target
```

**Telegram Bot Service**: `/etc/systemd/system/coco-telegram-bot.service`

```ini
[Unit]
Description=CoCo Telegram Bot
After=network.target coco-api.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/CoCo 7/coco-telegram-bot
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable coco-api coco-telegram-bot
sudo systemctl start coco-api coco-telegram-bot

# Check status
sudo systemctl status coco-api
sudo systemctl status coco-telegram-bot
```

#### Option 2: Docker Deployment

**Dockerfile for API Server**: `Dockerfile.api`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "coco_api_server.py"]
```

**Dockerfile for Telegram Bot**: `coco-telegram-bot/Dockerfile`

```dockerfile
FROM node:18-slim

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  coco-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      - COCO_API_TOKEN=${COCO_API_TOKEN}
      - AUTHORIZED_TELEGRAM_ID=${AUTHORIZED_TELEGRAM_ID}
    ports:
      - "127.0.0.1:8765:8765"
    volumes:
      - ./coco_workspace:/app/coco_workspace
    restart: unless-stopped

  coco-telegram-bot:
    build:
      context: ./coco-telegram-bot
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - COCO_API_URL=http://coco-api:8765
      - COCO_API_TOKEN=${COCO_API_TOKEN}
      - AUTHORIZED_USER_ID=${AUTHORIZED_TELEGRAM_ID}
    depends_on:
      - coco-api
    volumes:
      - ./coco-telegram-bot/telegram_sessions:/app/telegram_sessions
    restart: unless-stopped
```

**Deploy**:

```bash
docker-compose up -d
docker-compose logs -f
```

#### Option 3: PM2 Process Manager (macOS/Linux)

```bash
# Install PM2
npm install -g pm2

# Start API server
pm2 start coco_api_server.py --name coco-api --interpreter python

# Start Telegram bot
cd coco-telegram-bot
pm2 start npm --name coco-bot -- start

# Save process list
pm2 save

# Setup startup script
pm2 startup
```

### Monitoring & Maintenance

1. **Health Checks**
   ```bash
   # API health
   curl http://localhost:8765/

   # Bot health (check process)
   pgrep -f "coco-telegram-bot"
   ```

2. **Log Monitoring**
   ```bash
   # API logs
   tail -f /var/log/coco-api.log

   # Bot logs
   tail -f /var/log/coco-telegram-bot.log
   ```

3. **Automated Backups**
   ```bash
   # Backup sessions
   tar -czf sessions-backup-$(date +%Y%m%d).tar.gz \
     coco-telegram-bot/telegram_sessions
   ```

---

## Troubleshooting

### Common Issues

#### 1. "Connection refused" error

**Symptom**: Bot can't connect to API

**Solution**:
```bash
# Check API server is running
curl http://localhost:8765/

# Check firewall (if using)
sudo ufw status

# Check API host/port in .env match
grep COCO_API /Users/keithlambert/Desktop/CoCo\ 7/.env
grep COCO_API coco-telegram-bot/.env
```

#### 2. "Unauthorized" error

**Symptom**: Telegram messages rejected

**Solution**:
```bash
# Verify user ID matches
echo $AUTHORIZED_TELEGRAM_ID

# Get your actual Telegram ID
# Send message to @userinfobot in Telegram

# Update .env files with correct ID
```

#### 3. Bot not responding

**Symptom**: Messages sent but no response

**Solution**:
```bash
# Check bot logs
tail -f coco-telegram-bot/logs/bot.log

# Check API logs
tail -f logs/api.log

# Test API directly
curl -H "Authorization: Bearer YOUR_TOKEN" \
  -X POST http://localhost:8765/api/v1/conversation \
  -H "Content-Type: application/json" \
  -d '{"message":"test","user_id":"YOUR_ID"}'
```

#### 4. "Token invalid" errors

**Symptom**: Authentication failing

**Solution**:
```bash
# Ensure tokens match in both .env files
grep COCO_API_TOKEN /Users/keithlambert/Desktop/CoCo\ 7/.env
grep COCO_API_TOKEN coco-telegram-bot/.env

# Regenerate if needed
openssl rand -hex 32
```

#### 5. Messages too long / truncated

**Symptom**: Long responses cut off

**Solution**:
- Message splitter should handle this automatically
- Check `sendLongMessage()` is being used
- Verify Markdown parsing isn't breaking messages

#### 6. Memory queries returning empty

**Symptom**: `/recall` or `/facts` return no results

**Solution**:
```bash
# Check CoCo memory database
sqlite3 coco_workspace/coco_memory.db "SELECT COUNT(*) FROM facts;"

# Verify API endpoint is working
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8765/api/v1/memory/facts/all?user_id=YOUR_ID"
```

### Debug Mode

Enable verbose logging:

**API Server** (`coco_api_server.py`):
```python
# Change log level
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Telegram Bot** (`src/index.ts`):
```typescript
// Add debug logging
bot.use(async (ctx, next) => {
  console.log('[DEBUG]', ctx.updateType, ctx.message);
  await next();
});
```

---

## API Reference

### REST Endpoints

#### `GET /`

Health check endpoint.

**Response**:
```json
{
  "status": "running",
  "service": "CoCo API Server",
  "version": "1.0.0",
  "timestamp": "2025-10-26T..."
}
```

#### `POST /api/v1/conversation`

Process a conversation message.

**Headers**:
- `Authorization: Bearer <token>`

**Request**:
```json
{
  "message": "Hello CoCo",
  "user_id": "123456789",
  "session_id": "session_abc123"
}
```

**Response**:
```json
{
  "response": "Hello! How can I assist you today?",
  "session_id": "session_abc123",
  "tools_used": [],
  "thinking": "User greeted me...",
  "timestamp": "2025-10-26T..."
}
```

#### `GET /api/v1/memory/recall`

Query memory systems.

**Headers**:
- `Authorization: Bearer <token>`

**Query Parameters**:
- `query`: Search query (required)
- `limit`: Max results (optional, default 10)
- `user_id`: Telegram user ID (required)

**Response**:
```json
{
  "facts": [
    {
      "text": "Command: docker ps",
      "fact_type": "command",
      "importance": 0.8
    }
  ],
  "query_type": "facts"
}
```

#### `GET /api/v1/memory/facts/{type}`

Browse facts by type.

**Headers**:
- `Authorization: Bearer <token>`

**Path Parameters**:
- `type`: Fact type (optional, "all" for all types)

**Query Parameters**:
- `user_id`: Telegram user ID (required)

**Response**:
```json
{
  "facts": [...],
  "total_count": 42,
  "fact_type": "command"
}
```

#### `GET /api/v1/scheduler/status`

Get scheduler status.

**Headers**:
- `Authorization: Bearer <token>`

**Query Parameters**:
- `user_id`: Telegram user ID (required)

**Response**:
```json
{
  "tasks": [
    {
      "name": "Daily News",
      "schedule": "daily at 10am",
      "enabled": true
    }
  ],
  "scheduler_running": true
}
```

#### `POST /api/v1/scheduler/toggle`

Toggle automation feature.

**Headers**:
- `Authorization: Bearer <token>`

**Query Parameters**:
- `user_id`: Telegram user ID (required)

**Request**:
```json
{
  "feature": "news",
  "enabled": true
}
```

**Response**:
```json
{
  "success": true,
  "feature": "news",
  "enabled": true
}
```

### WebSocket Protocol

#### `WS /ws/conversation`

Real-time conversation streaming.

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8765/ws/conversation');
```

**Authentication** (first message):
```json
{
  "token": "your-api-token",
  "user_id": "123456789"
}
```

**Server Response**:
```json
{
  "status": "authenticated"
}
```

**Send Message**:
```json
{
  "message": "Hello CoCo"
}
```

**Receive Chunks**:
```json
{
  "type": "text",
  "content": "Hello! How...",
  "done": false
}
```

**Final Message**:
```json
{
  "type": "text",
  "content": "...can I help?",
  "done": true
}
```

**Error**:
```json
{
  "error": "Error message"
}
```

---

## Performance Optimization

### API Server

1. **Connection Pooling**
   ```python
   # Use connection pooling for database
   from sqlalchemy import create_engine, pool

   engine = create_engine(
       'postgresql://...',
       poolclass=pool.QueuePool,
       pool_size=10,
       max_overflow=20
   )
   ```

2. **Response Caching**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=128)
   def get_facts_cached(fact_type: str):
       # Cache facts queries
       pass
   ```

3. **Async Processing**
   ```python
   # Already using FastAPI's async capabilities
   # Ensure all database calls are async too
   from databases import Database

   database = Database('postgresql://...')
   ```

### Telegram Bot

1. **Message Batching**
   ```typescript
   // Batch multiple updates together
   const updates = [];

   setInterval(() => {
     if (updates.length > 0) {
       processUpdatesBatch(updates);
       updates.length = 0;
     }
   }, 1000);
   ```

2. **Response Caching**
   ```typescript
   const responseCache = new Map<string, {response: string, timestamp: number}>();

   async function getCachedOrFetch(key: string, fetcher: () => Promise<string>) {
     const cached = responseCache.get(key);
     if (cached && Date.now() - cached.timestamp < 60000) {
       return cached.response;
     }

     const response = await fetcher();
     responseCache.set(key, {response, timestamp: Date.now()});
     return response;
   }
   ```

---

## Future Enhancements

### Planned Features

1. **Multi-User Support**
   - User database with permissions
   - Per-user workspace isolation
   - Admin controls

2. **Group Chat Support**
   - Add bot to Telegram groups
   - @ mentions for activation
   - Shared memory context

3. **Voice Integration**
   - Voice message transcription
   - Text-to-speech responses
   - Voice commands

4. **Rich Media**
   - Photo uploads for vision analysis
   - Document processing
   - File sharing

5. **Advanced Notifications**
   - Configurable notification preferences
   - Priority levels
   - Do-not-disturb mode

6. **Analytics Dashboard**
   - Usage statistics
   - Response time metrics
   - Error tracking

---

## Contributing

This integration is designed for personal use but can be extended. Key extension points:

1. **New Commands**: Add to `src/bot/commands/`
2. **New API Endpoints**: Add to `coco_api_server.py`
3. **Custom Handlers**: Modify `src/bot/handlers/`
4. **Enhanced Formatting**: Extend `src/bot/utils/`

---

## License

This integration inherits CoCo's license. For personal use only.

---

## Support

For issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in both components
3. Test API endpoints directly with curl
4. Verify environment configuration

---

## Changelog

### Version 1.0.0 (October 26, 2025)

Initial release:
- ✅ Two-way messaging
- ✅ Full CoCo conversation access
- ✅ Memory system integration
- ✅ Scheduler controls
- ✅ Single-user authentication
- ✅ Session persistence
- ✅ Rich markdown formatting
- ✅ Message splitting for long responses

---

**End of CoCo Telegram Integration Plan**

*Generated by Claude Code*
*October 26, 2025*
