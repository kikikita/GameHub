# GameHub Backend Game Flow

This document describes how the game logic from the former Gradio
implementation was integrated into the FastAPI backend located in
`highway`.

## Overview

The legacy modules responsible for story generation, image and music
creation were moved under `src/game`. They keep the original logic but
now use settings from `src.game.config` and Redis configured via
`settings.redis_url`.

Game sessions and scenes are stored in PostgreSQL while the dynamic
state of the story is kept in Redis. The API exposes endpoints for
templates, sessions and scenes so that any frontend can interact with
the game engine purely over HTTP/WebSocket.

## Flow

1. **Template creation** – user defines setting, character and genre via
   `/api/v1/templates`.
2. **Session start** – POST `/api/v1/sessions` with a template ID.
   - A `GameSession` row is created.
   - Background music generation is started asynchronously.
   - The first scene is produced by `process_step(step="start")` using
     data from the chosen template.  The scene is saved in the `scenes`
     table.
3. **Current scene** – GET `/api/v1/sessions/{id}` returns the latest
   stored scene for the session.
4. **Choosing an option** – POST `/api/v1/sessions/{id}/choice` with the
   user text.  The choice is stored and `process_step(step="choose")`
   generates the next scene which is then stored.
5. **Audio streaming** – clients connect to
   `/api/v1/sessions/{id}/audio` (WebSocket) and receive continuous WAV
   chunks produced by Google Lyria via `update_audio`.
6. **History** – GET `/api/v1/sessions/{id}/history` returns the ordered
   list of all scenes for the session.
7. **Endings** – when `process_step` detects a game ending, the last
   scene contains the ending description and image. Further requests will
   not generate new scenes.

All scene descriptions, generated choices, images and user choices are
persisted allowing a complete replay of the story.
