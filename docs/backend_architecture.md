# Backend Architecture

This document provides an overview of the backend implemented in
`highway` and its interaction with the Telegram bot in `bot`.

## Application Layout

- **highway/src/main.py** – FastAPI application entry point. Routers from
  all API modules are registered here. CORS middleware is enabled and
  debugging via `debugpy` is supported when `debug_mode` is on.
- **highway/src/api/** – REST API divided into logical modules:
  - `auth` – registration and profile endpoints.
  - `templates` – CRUD for game templates.
  - `sessions` – management of game sessions and scene generation.
  - `scenes` – operations with individual scenes.
  - `payments` – simple subscription endpoints.
- **highway/src/auth/** – helper functions for verifying Telegram
  authentication data.
- **highway/src/core/** – database initialization and session provider.
- **highway/src/models/** – SQLAlchemy models describing persistent
  entities such as `User`, `GameTemplate`, and `GameSession`.
- **bot/** – aiogram based Telegram bot. Polls messages and delegates
  commands to handlers.

## External Dependencies

- **FastAPI** – main web framework.
- **SQLAlchemy** – asynchronous ORM for PostgreSQL/SQLite.
- **LangChain / Google Generative AI** – used for game scene generation.
- **Aiogram** – framework for building the Telegram bot.

## API Endpoints

Below is a brief summary of the public endpoints provided by FastAPI.

| Method | Path                                   | Description                          |
|-------|----------------------------------------|--------------------------------------|
| GET   | `/health-check`                        | Liveness probe.                      |
| POST  | `/auth/session`                        | Validate WebApp init data and set a cookie. |
| POST  | `/api/v1/auth/register`                | Register a Telegram user.            |
| GET   | `/api/v1/users/me`                     | Current user info.                   |
| POST  | `/api/v1/templates`                    | Create a game template.              |
| GET   | `/api/v1/templates`                    | List user templates.                 |
| GET   | `/api/v1/templates/{id}`               | Fetch a template.                    |
| POST  | `/api/v1/templates/{id}/share`         | Make a template public.              |
| GET   | `/api/v1/templates/shared/{code}`      | Retrieve shared template.            |
| POST  | `/api/v1/sessions`                     | Start a game session.                |
| GET   | `/api/v1/sessions/{id}`                | Get current scene.                   |
| POST  | `/api/v1/sessions/{id}/choice`         | Submit choice and generate next scene. |
| POST  | `/api/v1/sessions/{id}/scenes`         | Create additional scene.             |
| GET   | `/api/v1/sessions/{id}/history`        | Full session history.                |
| DELETE| `/api/v1/sessions/{id}`                | Remove game session.                 |
| GET   | `/api/v1/plans`                        | List available subscription plans.   |
| POST  | `/api/v1/subscribe`                    | Start subscription process.          |
| GET   | `/api/v1/subscription/status`          | Current subscription status.         |

## Telegram Bot Integration

The bot located in the `bot` directory communicates with the API by
sending HTTP requests using `httpx`. User authentication is performed
via Telegram WebApp `initData` which is later stored in a cookie by the
`/auth/session` endpoint. The bot uses custom keyboards and finite state
machines for a simple interactive adventure game.

