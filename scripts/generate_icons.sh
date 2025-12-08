#!/bin/bash
# PNG-Icons aus SVG generieren
# Benötigt: inkscape oder imagemagick (convert)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ICON_DIR="$PROJECT_ROOT/data/icons"
SVG_FILE="$ICON_DIR/mountrix-icon.svg"

# Prüfe ob inkscape oder imagemagick verfügbar ist
if command -v inkscape &> /dev/null; then
    CONVERTER="inkscape"
    echo "✓ Inkscape gefunden, nutze Inkscape für Konvertierung..."
elif command -v convert &> /dev/null; then
    CONVERTER="imagemagick"
    echo "✓ ImageMagick gefunden, nutze convert für Konvertierung..."
else
    echo "✗ Fehler: Weder Inkscape noch ImageMagick gefunden!"
    echo "  Installation:"
    echo "    Inkscape:    sudo apt install inkscape"
    echo "    ImageMagick: sudo apt install imagemagick"
    exit 1
fi

# Icon-Größen für verschiedene Zwecke
SIZES=(16 32 48 64 128 256 512)

echo "Generiere PNG-Icons in verschiedenen Größen..."

for SIZE in "${SIZES[@]}"; do
    OUTPUT="$ICON_DIR/mountrix-${SIZE}x${SIZE}.png"

    if [ "$CONVERTER" = "inkscape" ]; then
        inkscape "$SVG_FILE" \
            --export-filename="$OUTPUT" \
            --export-width=$SIZE \
            --export-height=$SIZE \
            2>/dev/null
    else
        convert "$SVG_FILE" \
            -resize ${SIZE}x${SIZE} \
            -background none \
            "$OUTPUT"
    fi

    if [ -f "$OUTPUT" ]; then
        echo "  ✓ ${SIZE}x${SIZE} erstellt"
    else
        echo "  ✗ ${SIZE}x${SIZE} fehlgeschlagen"
    fi
done

echo ""
echo "✓ Icon-Generierung abgeschlossen!"
echo "  Pfad: $ICON_DIR"
