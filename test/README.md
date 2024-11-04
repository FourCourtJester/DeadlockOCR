## Setup

Make sure you run these commands from the `workspace` folder, as they are all relative to that

### Upload a screenshot for Team Souls comparison

```bash
curl -X POST http://localhost:5000/deadlock/ocr/teams/souls -F 'image=@test/screenshot.jpg'
```

```json
{
  "souls": {
    "amber": 68,
    "delta": 8,
    "sapphire": 60
  }
}
```

```bash
curl -X POST http://localhost:5000/deadlock/ocr/teams/souls -F 'image=@test/hundredk_souls.jpg'
```

```json
{
  "souls": {
    "amber": 232,
    "delta": -15,
    "sapphire": 247
  }
}```

### Upload a screenshot for Player Names

```bash
curl -X POST http://localhost:5000/deadlock/ocr/teams/players -F 'image=@test/player_names.jpg'
```

```json
{
  "players": {
    "amber": [
      "below average player",
      "Greed",
      "NKD",
      "Lil Jimmy",
      "Full Synchro",
      "whiskers"
    ],
    "sapphire": [
      "Eidorian",
      "samch",
      "YUNG CALC",
      "Lonaw",
      "Walex :)",
      "hide on veil"
    ]
  }
}
```

```bash
curl -X POST http://localhost:5000/deadlock/ocr/teams/players -F 'image=@test/player_names_long.png'
```

```json
{
  "players": {
    "amber": [
      "Epindary",
      "dra\u00e9i bojovnik",
      "renegos",
      "Um_1n",
      "fink1337 mentality",
      "Tensai"
    ],
    "sapphire": [
      "Arial",
      "Godi",
      "deletgamtrash<3jk",
      "pixeNN",
      "DCLXVI",
      "mighty watermelon"
    ]
  }
}
```

```bash
curl -X POST http://localhost:5000/deadlock/ocr/teams/players -F 'image=@test/player_names_2lines.jpg'
```

```json
{
  "players": {
    "amber": [
      "confeti saati",
      "tyrker",
      "wassup",
      "141",
      "5up",
      "kENYF"
    ],
    "sapphire": [
      "Bass",
      "kk",
      "Cx",
      "Sovex",
      "pluxury",
      "TOM CRUISE OF DEADLOCK"
    ]
  }
}
```

### Upload a screenshot for Selected Player

```bash
curl -X POST http://localhost:5000/deadlock/ocr/camera -F 'image=@test/hundredk_souls.jpg'

curl -X POST http://localhost:5000/deadlock/ocr/camera -F 'image=@test/player_names_2lines.jpg'

curl -X POST http://localhost:5000/deadlock/ocr/camera -F 'image=@test/screenshot.jpg'
```

```json
{
  "camera": 11, // hundredk_souls.jpg
  "player": 5,
  "team": "Sapphire"
}
```

```json
{
  "camera": 4, // player_names_2lines.jpg
  "player": 4,
  "team": "Amber"
}
```

```json
{
  "camera": 9, // screenshot.jpg
  "player": 3,
  "team": "Sapphire"
}
```