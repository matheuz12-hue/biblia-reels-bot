import os, time, requests

IG_ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]
MP4_URL = os.environ["MP4_URL"]

GRAPH = "https://graph.facebook.com/v19.0"

def post(url, data):
    r = requests.post(url, data=data, timeout=60)
    try:
        j = r.json()
    except Exception:
        raise SystemExit(f"Non-JSON response: {r.status_code} {r.text}")
    if r.status_code >= 400:
        raise SystemExit(f"ERROR {r.status_code}: {j}")
    return j

def get(url, params=None):
    r = requests.get(url, params=params, timeout=60)
    j = r.json()
    if r.status_code >= 400:
        raise SystemExit(f"ERROR {r.status_code}: {j}")
    return j

def main():
    caption = "Reflexão bíblica do dia. #fe #biblia #reflexao"

    # 1) Create media container (Reels)
    container = post(
        f"{GRAPH}/{IG_USER_ID}/media",
        {
            "media_type": "REELS",
            "video_url": MP4_URL,
            "caption": caption,
            "access_token": IG_ACCESS_TOKEN,
        },
    )
    creation_id = container["id"]
    print("creation_id:", creation_id)

    # 2) Poll container status
    for _ in range(36):  # ~6 min (36 * 10s)
        status = get(
            f"{GRAPH}/{creation_id}",
            {
                "fields": "status_code,status",
                "access_token": IG_ACCESS_TOKEN,
            },
        )
        print("status:", status)
        sc = str(status.get("status_code", "")).upper()
        if sc in ("FINISHED", "READY", "PUBLISHED"):
            break
        if sc in ("ERROR", "FAILED"):
            raise SystemExit(f"Container failed: {status}")
        time.sleep(10)

    # 3) Publish
    published = post(
        f"{GRAPH}/{IG_USER_ID}/media_publish",
        {
            "creation_id": creation_id,
            "access_token": IG_ACCESS_TOKEN,
        },
    )
    print("published:", published)

if __name__ == "__main__":
    main()
