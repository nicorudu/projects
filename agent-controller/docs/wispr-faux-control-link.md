# Control link

> **Status: draft, tabled (2026-11-12).** Nothing is built yet.
> - **Nico's rule:** never edit the `nicorudu/wispr-faux` repo directly. The link goes into a **copy** of Wispr Faux inside this project ("Wispr Faux Controller", its own name and bundle ID); the original app and repo stay untouched.
> - **Open question:** does the copy replace the original on the Mac (one app, hotkey + controller), or run side by side (no hotkey, ~1–2 GB more memory, possible 2-minute model reloads)?
> - Paths in §6–7 refer to the Wispr Faux code layout and apply to the copy.


A private connection on this computer that lets another app use Wispr Faux as its dictation engine. The first user is the **AI Agent Controller** (this project): its Voice key asks Wispr Faux to listen, shows the text on the controller's dock for review, and only pastes it when you press Send.

The hotkey keeps working exactly as before. The link is a second way in.

Version 1 · Mac first, Windows after (same contract).

---

## 1. What it does

| The other app asks… | Wispr Faux… |
|---|---|
| **listen** | Records this computer's mic, with the usual pill. |
| **stop** | Transcribes and cleans up as usual, then sends the text **back** instead of pasting it. |
| **cancel** | Drops the recording or transcription. |
| **audio** (start, chunks, end) | Transcribes audio the other app recorded (the controller's own mics), with the same model, gate and cleanup. |
| **insert** | Pastes text into the focused app with the usual clipboard backup/restore and safety rules. It can press Return after, to send a prompt. |

Everything Wispr Faux already does stays in one place: Whisper large-v3 turbo, the speech gate, stumble cleanup and its guard, clipboard-safe paste, and history.

## 2. Connection

- **WebSocket** server on `ws://127.0.0.1:8767/`. Bound to loopback only, never to other interfaces.
- **Discovery file:** written at launch, readable only by the user (mode `0600`). It's removed on quit.
  - Mac: `~/Library/Application Support/Wispr Faux/control.json`
  - Windows: `%LOCALAPPDATA%\Wispr Faux\control.json`

  ```json
  {"v": 1, "port": 8767, "token": "<64 hex chars, new every launch>", "pid": 4242}
  ```
- **If port 8767 is taken,** use 8768–8775 (the first free one) and write the real port in the file. Clients always read the file.
- **Setting:** *Settings → General → Allow the agent controller to use Wispr Faux* (on by default). When it's off, there's no listener and no file.

### Security
1. **Origin header present → reject the handshake (HTTP 403).** Browsers always send `Origin`, so a web page can't reach the link. Native clients don't send it.
2. **The first message must be `hello` with the right token, within 2 s.** Otherwise close the connection (code 4401). Compare tokens in constant time.
3. **One client at a time.** A second client gets `error {code:"busy_client"}` and is closed. The first one keeps the link.
4. **Logs never contain words** (same rule as today): only ids, timings, lengths and outcomes.

## 3. Messages

JSON in text frames. Every message has `"v": 1` and a type `"t"`. Requests carry an `id` (string, chosen by the client); replies and events for that request carry the same `id`.

Audio for `audio_start` goes in **binary frames**: raw PCM, signed 16-bit little-endian, mono, 16 kHz, any chunk size. One audio stream at a time.

### Client → Wispr Faux

| `t` | Fields | Reply |
|---|---|---|
| `hello` | `client` (name, for logs), `token` | `welcome` |
| `listen` | `id` | `state listening`, then `level` events |
| `stop` | `id` | `state transcribing` → (`state cleaning`) → `result` |
| `cancel` | `id` | `cancelled` |
| `audio_start` | `id`, `rate` (must be 16000), `format` (must be `"s16le"`) | `state receiving` |
| *(binary frames)* | PCM | none |
| `audio_end` | `id` | `state transcribing` → (`state cleaning`) → `result` |
| `insert` | `id`, `text`, `submit` (bool, default false) | `inserted` |
| `ping` | `ts` (any number) | `pong` with the same `ts` |

### Wispr Faux → client

| `t` | Fields | When |
|---|---|---|
| `welcome` | `app: "wispr-faux"`, `version`, `platform: "mac"\|"windows"`, `model: "ready"\|"loading"\|"missing"`, `cleanup: "off"\|"local"\|"cloud"` | After a good `hello` |
| `state` | `id`, `state: "listening"\|"receiving"\|"transcribing"\|"cleaning"` | Each change |
| `level` | `id`, `level` (0…1, same as the pill's meter) | While listening, at most 10 per second |
| `result` | `id`, `text`, `spoken`, `cleaned` (bool), `audio_ms`, `transcribe_ms`, `cleanup_ms` | Done. If nothing usable was heard: `text: ""` and `reason: "too_short"\|"too_quiet"\|"nothing_heard"` |
| `cancelled` | `id` | After `cancel`, or Esc pressed on the Mac/PC while a link request was active |
| `inserted` | `id`, `outcome: "pasted"\|"copied"\|"refused"`, `reason` | After `insert` (see §4) |
| `error` | `id` (if any), `code`, `message` | See codes below |
| `pong` | `ts` | After `ping` |

`text` is what Wispr Faux would have pasted. `spoken` is the transcript before stumble cleanup, so the client can show both if they differ.

**Error codes:**
- `busy`: already listening or transcribing (for the hotkey or the link)
- `model_missing`
- `mic_denied`, `mic_unavailable`
- `too_long`: over the 5-minute cap; the audio so far is still transcribed
- `bad_request`: unknown type, missing field or wrong audio format
- `unknown_id`: `stop`, `cancel` or `audio_end` for an id that isn't active
- `busy_client`
- `internal`

## 4. Rules

- **Link results are added to History** like hotkey dictations (with `original` when cleanup changed them), so *Paste Last* and *Recent* keep working.
- **Link results are never pasted automatically.** Pasting only happens on `insert`.
- **The model is still loading:** `listen` works; the transcription waits for the model, exactly like a hotkey dictation does now. **The model is missing:** `listen` and `audio_start` reply `error model_missing`.
- **Hotkey vs link:** one recorder, so one dictation at a time. While a link request is active, the hotkey is ignored. While a hotkey dictation is active, link requests get `error busy`.
- **Esc** on the Mac/PC cancels an active link request too, and the client gets `cancelled`.
- **The pill** shows *Listening* / *Transcribing* for link requests as well, so you can see the mic is on. Notices like *Didn't hear anything* are not shown for link requests; the client shows them.
- **The client disconnects:** any active link request is cancelled and its audio dropped.
- **`insert`** follows today's insertion rules exactly:
  - password field → `refused`, nothing pasted or copied
  - no text field, or Accessibility can't tell → today's behavior (`pasted` for unknown, `copied` for not-text)
  - the clipboard is restored after 500 ms
  - a leading space is added when needed

  With `submit: true`, Return is pressed after the paste, 60 ms later. It's only pressed when `outcome` is `pasted`.
- **Speech gate:** the same thresholds (250 ms, −45 dBFS). For `audio_start` streams, the levels are computed from the received samples.

## 5. Example

```text
→ {"v":1,"t":"hello","client":"agent-controller","token":"9f…"}
← {"v":1,"t":"welcome","app":"wispr-faux","version":"0.7","platform":"mac","model":"ready","cleanup":"local"}
→ {"v":1,"t":"listen","id":"v1"}
← {"v":1,"t":"state","id":"v1","state":"listening"}
← {"v":1,"t":"level","id":"v1","level":0.42}            … up to 10/s
→ {"v":1,"t":"stop","id":"v1"}
← {"v":1,"t":"state","id":"v1","state":"transcribing"}
← {"v":1,"t":"state","id":"v1","state":"cleaning"}
← {"v":1,"t":"result","id":"v1","text":"Fix the login bug on Wednesday.","spoken":"Fix the login bug on Tuesday, no wait, Wednesday.","cleaned":true,"audio_ms":3400,"transcribe_ms":610,"cleanup_ms":540}
   … the controller's dock shows the text; you press Send …
→ {"v":1,"t":"insert","id":"v1-send","text":"Fix the login bug on Wednesday.","submit":true}
← {"v":1,"t":"inserted","id":"v1-send","outcome":"pasted"}
```

## 6. Implementation notes (Mac)

- **New module `ControlKit`** in `Packages/DictationKit`, with no AppKit. It holds:
  - message types (`Codable`), parsing and validation
  - token generation and constant-time compare
  - the discovery-file writer
  - an `s16le` → Float32 converter
  - unit tests for all of the above, plus every example message in this file
- **`ControlLinkServer`** in the app target: Network.framework `NWListener` with `NWProtocolWebSocket.Options`, `requiredLocalEndpoint` 127.0.0.1, and `Origin` checked in the WebSocket handshake callback (`setClientRequestHandler`).
- **`DictationController`** gets entry points that reuse the existing paths:
  - start/stop/cancel recording with a "return, don't paste" delivery, sharing `startRecording` / `finishRecording` / `prepare`
  - transcribe a `Recording` built from received samples (`levels` computed with the same `LevelStats` code)
  - `insert(text, submit)` through `insertOrCopy`, plus Return (keycode 36) for `submit`
- **Settings:** the toggle in General, and the discovery file written or removed when it changes.
- **Test from the command line** without the controller: `websocat` (`brew install websocat`), or the Python test client in the agent-controller repo (`tools/wispr_faux_client.py`).

## 7. Implementation notes (Windows, after the Mac)

- A WebSocket on loopback via `HttpListener` (`http://127.0.0.1:8767/`) with `AcceptWebSocketAsync`. Reject requests that have an `Origin` header.
- Same message types in `WisprFaux.Core` (testable), and the same rules.
- Return for `submit` via `SendInput` (VK_RETURN).
