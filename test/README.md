## Setup

Make sure you run these commands from the `workspace` folder, as they are all relative to that

### Upload a screenshot for Team Souls comparison

```bash
curl -X POST http://localhost:5000/deadlock/ocr/teams/souls -F 'image=@test/screenshot.jpg'
```