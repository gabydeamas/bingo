from spotify_scraper import SpotifyClient

# URL de tu playlist de Spotify
PLAYLIST_URL = "https://open.spotify.com/playlist/6Idv9ZafELT0OkMf3AQlt9?si=lgyhiPdHTzekDXMgUh8UhA"

def extraer_canciones(url, limite=None):
    """
    Extrae los nombres de las canciones de una playlist de Spotify
    sin necesidad de API key ni cuenta Premium.
    """
    with SpotifyClient() as client:
        # Obtener la playlist completa
        playlist = client.get_playlist(url, max_tracks=limite)
        
        # Extraer solo los nombres de las canciones
        canciones = []
        for item in playlist.tracks:
            if item.track:  # Algunos items pueden estar vacíos
                canciones.append(item.track.name)
        
        return canciones

if __name__ == "__main__":
    print("🎵 Extrayendo canciones de la playlist...")
    
    try:
        canciones = extraer_canciones(PLAYLIST_URL)
        
        # Guardar en un archivo de texto
        with open("canciones_bingo.txt", "w", encoding="utf-8") as f:
            for cancion in canciones:
                f.write(cancion + "\n")
        
        print(f"✅ ¡Listo! Se han extraído {len(canciones)} canciones.")
        print(f"📁 Guardadas en 'canciones_bingo.txt'")
        
        # Mostrar las primeras 5 como ejemplo
        print("\n📝 Canciones:")
        for i, c in enumerate(canciones, 1):
            print(f"  {i}. {c}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

