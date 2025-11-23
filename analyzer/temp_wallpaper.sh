#!/bin/bash

# --- Step 1: Cache ---
# Cache the current wallpaper URI
WALLPAPER_CACHE=$(gsettings get org.gnome.desktop.background picture-uri | cut -d \' -f 2-2)
echo "Caching original wallpaper: $WALLPAPER_CACHE"

# --- Step 2: Switch ---
# Define the temporary wallpaper path
NEW_WALLPAPER_PATH="/home/ian/lib/bin/simonsays/static/mad_wallpaper.png"

echo "Setting new wallpaper: $NEW_WALLPAPER_PATH"
gsettings set org.gnome.desktop.background picture-uri "file://$NEW_WALLPAPER_PATH"

# ** Pause here to do whatever you need to do **
# For demonstration, we'll just wait for a few seconds:
echo "Waiting for 5 seconds..."
sleep 5

# --- Step 3: Revert ---
echo "Reverting to original wallpaper: $WALLPAPER_CACHE"
gsettings set org.gnome.desktop.background picture-uri "$WALLPAPER_CACHE"

echo "Done."
