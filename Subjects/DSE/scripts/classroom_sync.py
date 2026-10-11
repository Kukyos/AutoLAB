"""Mirror a Google Classroom course locally: files into folders, links + metadata into index.md.
Usage: python classroom_sync.py [courseId]   (default: the DSE lab). Re-runnable; existing files are skipped."""
import glob, io, os, re, sys
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")  # google returns a reshuffled scope list; harmless
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")  # DSE/
SECRET = glob.glob(os.path.join(HERE, "..", "client_secret*.json"))[0]
TOKEN = os.path.join(HERE, "..", "token.json")
OUT = os.path.join(HERE, "materials", "classroom")
COURSE = sys.argv[1] if len(sys.argv) > 1 else "855460957674"
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.topics.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
# Google-native files can't be downloaded raw; export them.
EXPORT = {
    "application/vnd.google-apps.document": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
    "application/vnd.google-apps.presentation": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
    "application/vnd.google-apps.spreadsheet": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
}


def creds():
    c = Credentials.from_authorized_user_file(TOKEN, SCOPES) if os.path.exists(TOKEN) else None
    if not c or not c.valid:
        if c and c.refresh_token:
            c.refresh(Request())
        else:
            c = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES).run_local_server(port=0)
        open(TOKEN, "w").write(c.to_json())
    return c


def safe(s):
    return re.sub(r'[<>:"/\\|?*\n]+', "_", s).strip(" .") or "untitled"


def paged(method, key, **kw):
    tok = None
    while True:
        r = method(pageToken=tok, **kw).execute()
        yield from r.get(key, [])
        tok = r.get("nextPageToken")
        if not tok:
            return


def fetch(drive, f, folder):
    """Download one Drive file into folder; return a markdown line."""
    fid, title = f["id"], f.get("title") or f["id"]
    try:
        meta = drive.files().get(fileId=fid, fields="name,mimeType", supportsAllDrives=True).execute()
    except Exception as e:  # no access / deleted
        return f"- {title} (Drive {fid}): FAILED {e}"
    name, mime = safe(meta["name"]), meta["mimeType"]
    if mime in EXPORT:
        emime, ext = EXPORT[mime]
        name = name if name.endswith(ext) else name + ext
        req = drive.files().export_media(fileId=fid, mimeType=emime)
    elif mime.startswith("application/vnd.google-apps."):
        return f"- {title}: https://drive.google.com/open?id={fid} ({mime}, not downloadable)"
    else:
        req = drive.files().get_media(fileId=fid, supportsAllDrives=True)
    path = os.path.join(folder, name)
    if os.path.exists(path):
        return f"- {name} (already had)"
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    os.makedirs(folder, exist_ok=True)
    open(path, "wb").write(buf.getvalue())
    return f"- {name} ({len(buf.getvalue()) // 1024} KB)"


def main():
    c = creds()
    cr, dr = build("classroom", "v1", credentials=c), build("drive", "v3", credentials=c)
    topics = {t["topicId"]: t["name"] for t in paged(cr.courses().topics().list, "topic", courseId=COURSE)}
    items = [("Assignment", w) for w in paged(cr.courses().courseWork().list, "courseWork", courseId=COURSE)]
    items += [("Material", m) for m in paged(cr.courses().courseWorkMaterials().list, "courseWorkMaterial", courseId=COURSE)]
    rows = {}
    for kind, it in items:
        topic = topics.get(it.get("topicId"), "No topic")
        folder = os.path.join(OUT, safe(topic), safe(it["title"]))
        lines = []
        for m in it.get("materials", []):
            if "driveFile" in m:
                lines.append(fetch(dr, m["driveFile"]["driveFile"], folder))
            elif "link" in m:
                lines.append(f"- link: {m['link'].get('title', '')} {m['link']['url']}")
            elif "youtubeVideo" in m:
                lines.append(f"- video: {m['youtubeVideo'].get('title', '')} {m['youtubeVideo']['alternateLink']}")
            elif "form" in m:
                lines.append(f"- form: {m['form'].get('title', '')} {m['form']['formUrl']}")
        due = it.get("dueDate")
        due = f"{due['year']}-{due['month']:02}-{due['day']:02}" if due else ""
        rows.setdefault(topic, []).append(
            f"### {it['title']} ({kind}{', due ' + due if due else ''})\n{it.get('description', '').strip()}\n\n" + "\n".join(lines))
        print(topic, "/", it["title"], f"[{len(lines)} attachments]")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "index.md"), "w", encoding="utf-8") as fh:
        for t in sorted(rows):
            fh.write(f"## {t}\n\n" + "\n\n".join(rows[t]) + "\n\n")


if __name__ == "__main__":
    main()
