# Ibis Dash Quick Start Guide

## Setup

1. **Flash the firmware** to your ESP32-S3-PhotoPainter using Arduino IDE
2. **Run `Ibis.exe`** on your PC (board connected via USB)
3. **Follow the setup wizard** - enter WiFi, Strava credentials, your name, and goal
4. **Done!** Your Strava stats will appear on the display

You can change your preferences anytime by running `Ibis.exe` again.

---

## Buttons

| Button | What it does |
|--------|--------------|
| **BOOT** | Refresh - fetches new data from Strava |
| **KEY** | Nothing (yet) |
| **PWR** | Hold 4 seconds to power off |

---

## Battery Life

| Refresh Rate | Battery Life |
|--------------|--------------|
| Hourly | 3-5 days |
| Every 6 hours | 2-3 weeks |
| Every 12 hours | ~1 month |
| Daily | ~2 months |
| Every 2 days | 3-4 months |
| Weekly | 6+ months |

---

## Battery Indicator

- **Blue headers** = Low battery (charge soon!)
- **Red corner with %** = Battery percentage when low
- **"I-MUUT! 100%"** = Fully charged on USB

---

## Need to Change Settings?

1. Connect board to PC via USB
2. Run `Ibis.exe`
3. Update your preferences
4. Click "Finish Setup"

---

## Need to Wipe Everything?

**Option 1:** In `Ibis.exe` → Options tab → "Wipe Data"

**Option 2:** Hold BOOT button for 5 seconds during startup

---

## Questions?

Check the full README.md for detailed troubleshooting and setup instructions.
