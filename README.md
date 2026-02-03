# 🪶 Ibis Dash - Strava E-Paper Dashboard

An e-paper dashboard that shows your Strava stats. Written with a ton of frustration, mass amounts of trial and error, and the help of Claude. But hey, it works now!

---

## What It Does

Shows your running/cycling/swimming/hiking/walking stats on a nice e-ink screen. Distance, time, activity count, your route, progress toward your yearly goal. Updates automatically. Runs on battery for weeks. Looks cool on your desk.

That's it. That's the project.

---

## What I Used

- **Waveshare ESP32-S3-PhotoPainter** - comes with the 7.5" color e-paper display already attached, LiPo battery, and USB-C cable all included
- **Arduino IDE** - free
- **Ibis Setup app** - included here, also free (I made it)
- **A Strava account** - you probably have one if you're here

---

## How Hard Is This?

If you can follow instructions, you can do this. The actual coding part is done - you just upload my code to the board and configure it with the app. No coding required on your end.

The "hardest" part is getting Strava API credentials, and even that takes like 5 minutes.

---

## Setup (The Short Version)

1. Install Arduino IDE
2. Add ESP32 board support
3. Install some libraries (GxEPD2, ArduinoJson, XPowersLib, QRCode)
4. Set the right board settings (see below - this part matters!)
5. Upload `IBIS_V31.ino` to your board
6. Open `Ibis.exe`, connect, enter WiFi + Strava credentials
7. Done. Go for a run.

---

## Arduino IDE Settings

⚠️ **Get these right or your board will be sad:**

| Setting | Value |
|---------|-------|
| Board | ESP32S3 Dev Module |
| USB CDC On Boot | Disabled |
| Flash Mode | **DIO** (NOT OPI!) |
| Flash Size | 16MB (128Mb) |
| PSRAM | OPI PSRAM |
| Partition Scheme | 16M Flash (3MB APP/9.9MB FATFS) |

The Flash Mode one is important. Ask me how I know.

---

## Getting Strava API Stuff

1. Go to [strava.com/settings/api](https://www.strava.com/settings/api)
2. Create an app (name it whatever, set callback domain to `localhost`)
3. Copy the Client ID and Client Secret into the Ibis Setup app
4. Click "Get Refresh Token" - it opens a browser, you authorize, done

---

## Buttons

| Button | What it does |
|--------|--------------|
| KEY | Absolutely nothing. It's there for vibes. |
| BOOT | Force screen refresh and data fetch |
| PWR | Power on/off |

---

## What's In Here

```
ibis-dash/
├── firmware/
│   ├── IBIS_V31.ino    ← The Arduino code
│   └── ibis_logos.h    ← Pixel art logos (yes I made these)
├── app/
│   ├── Ibis.exe        ← Windows setup app
│   └── Ibis.py         ← Python source if you're curious
├── docs/
│   └── USER_MANUAL.md  ← More detailed instructions if you get stuck
├── README.md           ← You are here
└── LICENSE             ← MIT-ish, see below
```

---

## Why "Ibis"?

Because, believe it or not, I am a bird. 🪶

---

## License

MIT - use it, modify it, make it better. Just don't make it commercial without my consent.

---

## Credits

Built with [GxEPD2](https://github.com/ZinggJM/GxEPD2), [ArduinoJson](https://arduinojson.org/), [XPowersLib](https://github.com/lewisxhe/XPowersLib), the Strava API, mass debugging, mass coffee, and mass vibes.

Shoutout to Nerdland and some fellow nerds. 🤓

---

Happy tracking! 🏃‍♂️🪶
