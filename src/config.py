"""
Configuration and magic constants for Humbug

"""
# Assumes you run from inside the annex
ANNEX_LOCATION = './'

# Subdirectories of the annex where you keep different kinds of file
BOOKS_SUBDIR = 'Books/Humble Bundle/'
GAMES_SUBDIR = 'Games/'
MOVIES_SUBDIR = 'Videos/Movies/'

# Games are stored in
# {ANNEX_LOCATION}/{GAMES_SUBDIR}/{game.title}/{TYPE_SUBDIR}/{filename}
# with TYPE_SUBDIR indicating the OS and architecture the file was
# built for. Each game has builds for a subset of the below OS/arch.
GAME_TYPE_SUBDIR = {
    'android': 'Android',
    'windows': 'Windows - i386',
    'linux': {
        '64-bit': 'Linux - x86_64',
        '32-bit': 'Linux - i386',
        },
    'mac': 'OSX',
    'mac10.5': 'OSX 10.5',
    'mac10.6+': 'OSX 10.6+',
    'air': 'Air',
    'flash': 'Flash',
    'audio': 'Soundtrack',
}

# Modifications to names given in the Humble Bundle, for a cleaner annex.
# See also HumbugHandler.clean_name.
NAME_EXCEPTIONS = {
    # Penumbra Overture is really "Penumbra: Overture", which should
    # be a hyphen as above.
    'Penumbra Overture': 'Penumbra - Overture',

    # Don't keep prefix'd "The", and downcase 'Of'
    'The Binding Of Isaac': 'Binding of Isaac',
    'The Binding of Isaac + Wrath of the Lamb DLC': 'Binding of Isaac + Wrath of the Lamb DLC',

    # Rename this to be Introversion-specific
    'City Generator Tech Demo': 'Introversion City Generator Demo',

    # Correct capitalization according to website.
    'FTL - Faster than Light': 'FTL - Faster Than Light',
    # Correct capitalization, according to World of Goo website
    'World Of Goo': 'World of Goo',
}

UNPACKED_NAMES = {
    'Kooky/Highest Quality MP4': 'Kooky [Top quality, 720p].mp4',
    'Kooky/Recommended MP4': 'Kooky [Normal quality, 720p].mp4',
}

SOUNDTRACK_TYPES = ['MP3', 'FLAC', 'WAV', 'OGG']
