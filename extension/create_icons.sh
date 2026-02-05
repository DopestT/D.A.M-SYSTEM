#!/bin/bash
# Create simple placeholder icons using ImageMagick if available, or base64 encoded data

# Check if convert (ImageMagick) is available
if command -v convert &> /dev/null; then
    # Create icons with ImageMagick
    convert -size 16x16 xc:'#1a1a2e' -fill '#00d4ff' -draw "rectangle 4,4 12,12" icon16.png
    convert -size 48x48 xc:'#1a1a2e' -fill '#00d4ff' -draw "rectangle 12,12 36,36" icon48.png
    convert -size 128x128 xc:'#1a1a2e' -fill '#00d4ff' -draw "rectangle 32,32 96,96" icon128.png
    echo "Icons created with ImageMagick"
else
    # Create minimal PNG files with base64 data
    # These are valid 1x1 PNGs that can be used as placeholders
    echo "Creating minimal placeholder icons..."
    
    # Decode base64 to create a valid PNG
    # This is a 16x16 blue square PNG
    base64 -d > icon16.png << 'ICON16'
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAAWdEVYdENyZWF0aW9uIFRpbWUAMDcvMTMvMTJJ/SWIAAAAHElEQVQ4jWNgGAWjYBSMglEwCkbBKBgFQx8AAAKHAAGK9sJNAAAAAElFTkSuQmCC
ICON16

    # Copy for other sizes
    cp icon16.png icon48.png
    cp icon16.png icon128.png
    
    echo "Placeholder icons created"
fi
