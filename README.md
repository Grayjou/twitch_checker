# Twitch Checker

[![PyPI version](https://img.shields.io/pypi/v/twitch-checker.svg)](https://pypi.org/project/twitch-checker/)
[![Python versions](https://img.shields.io/pypi/pyversions/twitch-checker.svg)](https://pypi.org/project/twitch-checker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-level Twitch stream checker with state tracking and change detection. Monitor multiple Twitch streamers efficiently with asynchronous requests and smart state management.

## Features

- 🚀 **Asynchronous** - Built with `aiohttp` for high-performance concurrent checks
- 🔄 **State Tracking** - Tracks online/offline transitions with configurable cooldowns
- 🎯 **Change Detection** - Detects when streamers go live or go offline
- 📦 **Batch Processing** - Checks up to 100 streamers per API call
- 💾 **Persistence** - Save and restore monitoring state between sessions
- ✅ **Validation** - Automatically filters out non-existent usernames
- 🛡️ **Robust** - Handles rate limits and automatic token refresh
- 🐍 **Typed** - Full type annotations for better development experience

## Installation

```bash
pip install twitch-checker
```

## Quick Start

```python
import asyncio
from twitch_checker import TwitchChecker

async def main():
    # Initialize with your Twitch API credentials
    checker = TwitchChecker(
        client_id="your_client_id",
        client_secret="your_client_secret",
        logins=["shroud", "ninja", "pokimane"]
    )
    
    # Check current status
    statuses = await checker.check_logins()
    
    for status in statuses:
        print(f"{status.login}: {'LIVE' if status.is_live else 'offline'} {status.change or ''}")

asyncio.run(main())
```

## Configuration

### Environment Variables (Recommended)

```bash
export TWITCH_CLIENT_ID="your_client_id"
export TWITCH_CLIENT_SECRET="your_client_secret"
```

### Direct Initialization

```python
checker = TwitchChecker(
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

> **Get Twitch API Credentials:**
> 1. Go to [Twitch Console](https://dev.twitch.tv/console)
> 2. Create a new application
> 3. Copy Client ID and generate Client Secret

## Usage Examples

### Basic Monitoring

```python
checker = TwitchChecker(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    logins=["streamer1", "streamer2", "streamer3"]
)

# Check once
statuses = await checker.check_logins()

# Check periodically
while True:
    statuses = await checker.check_logins()
    for status in statuses:
        if status.change == "UP":
            print(f"🎉 {status.login} just went live!")
        elif status.change == "DOWN":
            print(f"😴 {status.login} went offline")
    await asyncio.sleep(60)  # Check every minute
```

### Using Cooldowns

```python
# Wait 5 minutes before reporting offline status
checker = TwitchChecker(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    logins=streamers,
    cooldown_seconds=300  # 5 minutes
)
```

This prevents false offline notifications when a streamer briefly disconnects or has internet issues.

### Classifying Streamers

```python
# Check which streamers exist and their current status
classification = await checker.classify_logins([
    "existing_streamer", "nonexistent_user", "another_streamer"
])

# Result:
# {
#     "existing_streamer": "exists_and_live",
#     "nonexistent_user": "does_not_exist", 
#     "another_streamer": "exists_but_not_live"
# }
```

### Persistent State

```python
# Save state to file
checker.export_json("state.json")

# Later, restore state
checker = TwitchChecker.from_json(
    "state.json",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
```

## API Reference

### TwitchChecker

**`__init__(client_id, client_secret, logins=None, *, cooldown_seconds=0, checked_existence=None)`**

- `client_id`: Twitch API Client ID
- `client_secret`: Twitch API Client Secret  
- `logins`: Initial list of streamer logins to monitor
- `cooldown_seconds`: Delay before reporting offline status (prevents false positives)
- `checked_existence`: Pre-validated usernames (internal use)

**Methods:**

- `async check_logins() -> Set[StreamerStatus]`: Check all monitored streamers
- `async classify_logins(logins) -> Dict[str, str]`: Categorize streamers by existence/live status
- `async batch_user_exists(logins) -> Set[str]`: Check which usernames exist
- `export_json(path) -> str`: Save state to JSON file
- `classmethod from_json(path, *, client_id, client_secret)`: Load state from JSON file

### StreamerStatus

- `login`: Streamer's username
- `is_live`: Current live status (True/False)
- `change`: Status change ("UP", "DOWN", or None)
- `data`: Raw Twitch API stream data

## Advanced Usage

### Integrating with Discord Bots

```python
import discord
from twitch_checker import TwitchChecker

class TwitchCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checker = TwitchChecker(CLIENT_ID, CLIENT_SECRET)
        self.checker.logins = ["favorite_streamers..."]
        
    async def twitch_loop(self):
        while True:
            statuses = await self.checker.check_logins()
            for status in statuses:
                if status.change == "UP":
                    channel = self.bot.get_channel(NOTIFICATION_CHANNEL_ID)
                    await channel.send(
                        f"🔴 **{status.login}** just went live!\n"
                        f"https://twitch.tv/{status.login}"
                    )
            await asyncio.sleep(120)
```

### Error Handling

```python
try:
    statuses = await checker.check_logins()
except Exception as e:
    print(f"Error checking streamers: {e}")
    # Handle rate limits, authentication errors, etc.
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have questions:

1. Check the [Twitch API Documentation](https://dev.twitch.tv/docs/api/)
2. Open an [issue on GitHub](https://github.com/Grayjou/twitch_checker/issues)
3. Ensure your API credentials are correct and have the necessary permissions

## Acknowledgments

- [Twitch](https://dev.twitch.tv/) for providing the API
- [aiohttp](https://docs.aiohttp.org/) for async HTTP requests
- The Python community for excellent tooling and support
```

These files provide:

**CHANGELOG.md:**
- Professional format following Keep a Changelog standards
- Clear breakdown of what's included in the initial release
- Semantic versioning ready for future updates

**README.md:**
- Professional branding with badges (will work once published)
- Clear installation and setup instructions
- Multiple usage examples for different scenarios
- Comprehensive API documentation
- Practical integration examples (like Discord bots)
- Troubleshooting and support sections
- Contributing guidelines

The README is designed to help users get started quickly while also providing depth for advanced use cases. It covers everything from basic monitoring to persistent state management and error handling.