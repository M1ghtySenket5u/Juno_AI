"""Linux Mint trivia for Juno's startup greeting — facts are general knowledge, not time-sensitive."""

import random

MINT_FUN_FACTS: tuple[str, ...] = (
    "Linux Mint began as a variant of Ubuntu with codecs and proprietary drivers made easier out of the box.",
    "The Mint team ships three desktop flavors today: Cinnamon (flagship), MATE, and Xfce — each tuned for different hardware and tastes.",
    "Cinnamon is Mint's own desktop shell: it's familiar if you're coming from Windows and stays very configurable.",
    "Update Manager on Mint ranks updates by stability so newcomers can see what's 'safer' versus more cutting-edge.",
    "Timeshift is integrated with Mint so you can roll back the whole system after a bad update — like a time machine for your OS.",
    "Mint's Software Manager is a friendly front-end to packages: less terminal-first than some distros, but the same underlying tools.",
    "The Mint motto is often summarized as 'freedom and elegance' — practical daily computing with polish.",
    "Mint avoids some controversial directions other desktops took; the project listens closely to its user base.",
    "You can run Mint entirely from a USB stick to try it before installing — great for testing Wi-Fi and graphics.",
    "Flatpak support in Mint means newer app versions without waiting for the whole distribution to move forward.",
    "The classic green Mint branding is iconic, but themes let you restyle the whole desktop in minutes.",
    "Mint is based on Ubuntu LTS releases for its main edition, which means a predictable support cycle for packages.",
    "The 'Edge' ISO sometimes ships a newer kernel for very new hardware — handy if live USB won't boot otherwise.",
    "Mint's welcome screen can walk you through drivers, snapshots, and desktop basics on first boot.",
    "Nemo is Cinnamon's file manager: split panes, tabs, and scriptable actions are all there if you dig in.",
    "Minttools (like mintdrivers) are small utilities that glue hardware, repos, and settings into one-click workflows.",
    "Community editions have explored other bases in the past; checking mint.com is the source of truth for what's current.",
    "Synaptic still exists for power users who want a raw view of every package and dependency.",
    "Mint's forums and monthly blog posts are first-class places to read release notes and upcoming changes.",
    "You can theme GTK, icons, and cursors separately — so 'galaxy samurai NASA' at home is absolutely allowed.",
)


def random_mint_fact() -> str:
    return random.choice(MINT_FUN_FACTS)
