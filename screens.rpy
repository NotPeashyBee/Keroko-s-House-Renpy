# ------------------------
# screens.rpy
# ------------------------
init python:
    import time, random

    # ------------------------
    # Persistent defaults
    # ------------------------
    def ensure_keroko():
        """Ensure Keroko persistent data exists with default fields."""
        defaults = {
            "happiness": 60,
            "hunger": 40,
            "energy": 70,
            "apples": 3,
            "last_action": "None",
            "start_timestamp": time.time(),
            "last_timestamp": time.time(),
        }

        if not hasattr(persistent, "keroko") or not isinstance(persistent.keroko, dict):
            persistent.keroko = defaults.copy()
        else:
            for k, v in defaults.items():
                if k not in persistent.keroko:
                    persistent.keroko[k] = v
        return persistent.keroko

    # ------------------------
    # Natural decay
    # ------------------------
    def update_stats():
        """Apply natural decay to hunger, energy, and happiness."""
        st = ensure_keroko()
        now = time.time()
        elapsed_minutes = (now - st["last_timestamp"]) / 60.0

        # Hunger increases gradually over time
        st["hunger"] = min(100, st["hunger"] + int(elapsed_minutes * 0.5))
        # Energy decreases gradually over time
        st["energy"] = max(0, st["energy"] - int(elapsed_minutes * 0.4))
        # Happiness drops if hunger high or energy low
        st["happiness"] = max(0, st["happiness"] - int(elapsed_minutes*0.2) - int(st["hunger"]/100*2))
        st["last_timestamp"] = now
        return st

    # ------------------------
    # Day calculation
    # ------------------------
    def get_day():
        st = ensure_keroko()
        return int((time.time() - st["start_timestamp"]) // 86400) + 1

    # ------------------------
    # Generic action handler
    # ------------------------
    def perform_action(happiness=0, hunger=0, energy=0, apples=0, msg=""):
        st = update_stats()
        st["happiness"] = max(0, min(100, st["happiness"] + happiness))
        st["hunger"] = max(0, min(100, st["hunger"] + hunger))
        st["energy"] = max(0, min(100, st["energy"] + energy))
        st["apples"] = max(0, st["apples"] + apples)
        st["last_action"] = msg
        st["last_timestamp"] = time.time()
        renpy.notify(msg)
        try:
            renpy.save("1")
        except:
            pass

    # ------------------------
    # Specific actions
    # ------------------------
    def pat_keroko():
        perform_action(happiness=10, msg="Patted Keroko")

    def feed_apple():
        st = ensure_keroko()
        if st["apples"] > 0:
            perform_action(happiness=15, hunger=-25, apples=-1, msg="Fed an apple")
        else:
            renpy.notify("No apples left!")

    def watch_tv():
        perform_action(happiness=10, energy=-5, msg="Watched TV")

    def sleep():
        perform_action(happiness=5, hunger=15, energy=35, msg="Slept")

    def buy_apple():
        perform_action(apples=1, msg="Bought an apple")

# ------------------------
# HUD Styles
# ------------------------
init -2 python:
    style.hud_title = Style(style.default)
    style.hud_title.size = 22
    style.hud_title.bold = True
    style.hud_title.outlines = [(2,"#000000",0,0)]
    style.hud_title.xalign = 0.5

    style.hud_stat_text = Style(style.default)
    style.hud_stat_text.size = 18
    style.hud_stat_text.color = "#ffffff"
    style.hud_stat_text.outlines = [(2,"#000000",0,0)]
    style.hud_stat_text.xalign = 0.0

    style.hud_bar_text = Style(style.default)
    style.hud_bar_text.size = 16
    style.hud_bar_text.color = "#ffff00"
    style.hud_bar_text.outlines = [(2,"#000000",0,0)]
    style.hud_bar_text.xalign = 0.0

# ------------------------
# HUD Screen
# ------------------------
screen keroko_hud():
    tag keroko_hud
    zorder 100

    $ st = ensure_keroko()

    frame:
        background Solid("#2e8b57cc")
        padding (12,12,12,12)
        xmaximum 320
        xalign 0.98
        yalign 0.5
        has vbox

        text "Keroko's House" style "hud_title"

        hbox:
            spacing 8
            text "Day: [get_day()]" style "hud_stat_text"
            text "Apples: [st['apples']]" style "hud_stat_text"

        vbox:
            spacing 4
            text "Happiness: [st['happiness']]" style "hud_stat_text"
            text "[('#'*int(st['happiness']/100*20))]" style "hud_bar_text"

            text "Hunger: [st['hunger']] (higher = hungrier)" style "hud_stat_text"
            text "[('#'*int(st['hunger']/100*20))]" style "hud_bar_text"

            text "Energy: [st['energy']]" style "hud_stat_text"
            text "[('#'*int(st['energy']/100*20))]" style "hud_bar_text"

        text "Last: [st['last_action']]" style "hud_stat_text"

        hbox:
            spacing 6
            textbutton "Feed Apple" action Function(feed_apple)
            textbutton "Watch TV" action Function(watch_tv)
            textbutton "Sleep" action Function(sleep)

        hbox:
            spacing 6
            textbutton "Buy Apple" action Function(buy_apple)
            textbutton "Restart Game" action Jump("main_menu")

# ------------------------
# Keroko Displayable
# ------------------------
init python:
    class KerokoDisplayable(renpy.Displayable):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.image = "keroko neutral"
            self._last_click = 0
            self._img_data = None

        def render(self,width,height,st,at):
            xpos = width/2
            ypos = height/2

            img = renpy.exports.displayable(self.image).render(width,height,st,at)
            render = renpy.Render(width,height)
            render.blit(img,(xpos-img.width/2,ypos-img.height/2))
            self._img_data = (xpos,ypos,img.width,img.height)
            return render

        def event(self,ev,x,y,st):
            if getattr(ev,"type",None)=="mousedown":
                now = time.time()
                if now - self._last_click < 0.3:
                    return False
                self._last_click = now
                if self._img_data:
                    xpos,ypos,iw,ih = self._img_data
                    sx = xpos-iw/2
                    sy = ypos-ih/2
                    if sx<=x<=sx+iw and sy<=y<=sy+ih:
                        pat_keroko()
                        return True