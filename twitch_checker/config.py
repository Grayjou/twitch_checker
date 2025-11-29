"""
Configuration module for Twitch API credentials.
"""
USE_OS = True # Set to True to load credentials from environment variables
if USE_OS:
    import os

    CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

    if not CLIENT_ID:
        CLIENT_ID = None

    if not CLIENT_SECRET:
        CLIENT_SECRET = None
else:
    CLIENT_ID = None # Replace with your Twitch Client ID or set it in the main class init
    CLIENT_SECRET = None # Replace with your Twitch Secret or set it in the main class init
