# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-28 (YYYY-MM-DD)

### Added
- **Initial release** of Twitch Checker package
- `TwitchChecker` class for monitoring Twitch streamer status
- Asynchronous API wrapper with automatic token management
- State tracking with cooldown periods for offline transitions
- Batch processing for efficient API usage
- Streamer existence validation
- Serialization support for persistent state
- Classification utility for categorizing streamer status
- Comprehensive type hints throughout the codebase

### Features
- Real-time stream status monitoring
- Change detection (UP/DOWN transitions)
- Cooldown mechanism to prevent false offline notifications
- Batch operations for multiple streamers (up to 100 per API call)
- Automatic retry and token refresh for API calls
- Environment variable configuration support
- JSON import/export for persistent state

### Technical
- Built with `aiohttp` for asynchronous HTTP requests
- Python 3.7+ compatibility
- Full type annotations
- MIT licensed