# ------------------------
# script.rpy
# ------------------------
define config.developer = True
define e = Character(None, kind=centered)

# ------------------------
# Images
# ------------------------
image bg room = "images/bg_room.jpg" if renpy.file("images/bg_room.jpg") else Solid("#dfeff2")
image keroko neutral = "images/character/keroko.png" if renpy.file("images/character/keroko.png") else Solid("#88cc66")
image apple = "images/apple.png" if renpy.file("images/apple.png") else Solid("#ff6666")
image tv = "images/tv.png" if renpy.file("images/tv.png") else Solid("#444444")

# ------------------------
# Labels
# ------------------------
label splashscreen:
    scene bg room
    show keroko neutral
    with dissolve
    "A small, cozy room. A girl in a froggy raincoat — Keroko — sits on a cushion."

    menu:
        "Start playing":
            jump main_room
        "Go to title screen":
            jump main_menu

label main_menu:
    scene bg room
    centered "KEROKO'S HOUSE"
    centered "A tiny Tamagotchi-style Ren'Py game"

    menu:
        "Start / Continue":
            jump main_room
        "Reset (clear saved persistent data)":
            $ persistent.keroko = None
            $ ensure_keroko()
            "All saved Keroko data has been reset."
            jump main_menu
        "Quit":
            $ renpy.quit()

label main_room:
    scene bg room
    show expression KerokoDisplayable() as keroko_sprite with dissolve

    call screen keroko_hud

    "You step back and watch Keroko for a moment."

    # ------------------------
    # Main loop: natural decay and idle
    # ------------------------
    while True:
        $ update_stats()
        # Optionally display a small idle message depending on stats
        $ st = ensure_keroko()
        if st["hunger"] > 80:
            "Keroko looks very hungry..."
        elif st["energy"] < 20:
            "Keroko is sleepy..."
        elif st["happiness"] < 30:
            "Keroko seems sad..."
        pause 5