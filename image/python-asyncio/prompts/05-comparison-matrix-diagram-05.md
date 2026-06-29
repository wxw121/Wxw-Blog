---
layout: comparison-matrix
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Table or matrix comparison layout
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌──────────────────────────────────────────────────────┐
│              同步库              │      异步替代       │
├──────────────────────────────────┼────────────────────┤
│  requests                        │  aiohttp / httpx   │
│  sqlalchemy (orm)                │  sqlalchemy[asyncio]│
│  psycopg2 (postgresql)           │  asyncpg            │
│  redis-py                        │  redis-py (内置async)│
│  pymongo                         │  motor              │
│  beautifulsoup4                  │  aiohttp + bs4      │
│  openai (python sdk)             │  AsyncOpenAI        │
│  boto3 (aws)                     │  aioboto3           │
│  kafka-python                    │  aiokafka           │
│  websocket-client                │  websockets         │
│  django                          │  FastAPI / Starlette│
│  flask                           │  FastAPI / aiohttp  │
└──────────────────────────────────┴────────────────────┘