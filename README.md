# ktl-report-daily

Automated daily NFL videos for the **KTL Report** channel (youtube.com/@KTLReport).

Same engine as `knicks-auto-daily` and `nba-tunnel-daily`; everything that makes
this channel different lives in `channel.json` — team, roster, sources, voice,
edit rhythm. No code changes are needed to point it at another team.

## Before the first run

1. Fill in `channel.json`: `team`, `nickname`, `venue`, `hashtags`, `roster`.
2. Secrets (Settings -> Secrets and variables -> Actions):
   `ANTHROPIC_API_KEY`, `GOOGLE_TTS_KEY`, `ADMIN_PAT`,
   `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
3. Releases: upload the team's stock footage as a release tagged `broll`,
   and the background music as a release tagged `music`.

## Schedule (Istanbul)

| run | starts | uploaded by | publishes |
|-----|--------|-------------|-----------|
| morning   | 04:00 | 06:00 | 11:00 |
| afternoon | 13:00 | 15:00 | 18:00 |

Thumbnails are not generated. After every upload the workflow opens a
"KAPAK GEREKLI" issue with the title, the publish time, the Studio link and the
most-mentioned player, so the cover can be designed by hand.
