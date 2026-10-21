#!/usr/bin/env python3
"""Gera audiobook PT-BR (Edge TTS / AntonioNeural) dos artigos do blog.
Uso: python3 tools/gen-audio.py [slug ...]   # sem args = todos os posts PT
"""
import pathlib, re, subprocess, sys, html

PT_VOICE = "pt-BR-AntonioNeural"
CONTENT = pathlib.Path("content/pt/posts")
STATIC = pathlib.Path("static/audio/pt")
RATE = "+0%"

def md_to_speech(md: str) -> str:
    # remove frontmatter
    md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)
    # blocos de código: cues curtos
    md = re.sub(r"```[a-z]*\n.*?\n```", " [Trecho de código exibido no artigo.] ", md, flags=re.S)
    # tabelas -> frases faláveis
    out_lines = []
    for ln in md.splitlines():
        s = ln.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and all(re.fullmatch(r"[-: ]+", c or "-") for c in cells):
                continue  # separador
            out_lines.append(". ".join(c for c in cells if c) + ".")
        else:
            out_lines.append(ln)
    md = "\n".join(out_lines)
    # imagens e links
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    md = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)
    # ênfase
    md = re.sub(r"\*\*\*([^*]+)\*\*\*", r"\1", md)
    md = re.sub(r"\*\*([^*]+)\*\*", r"\1", md)
    md = re.sub(r"\*([^*]+)\*", r"\1", md)
    md = re.sub(r"_([^_]+)_", r"\1", md)
    # títulos viram frases
    md = re.sub(r"^#{1,6}\s*(.+)$", lambda m: m.group(1) + ".\n", md, flags=re.M)
    # cores inline sobram em texto corrido
    md = re.sub(r"`([^`]*)`", r"\1", md)
    md = html.unescape(md)
    # normalizações de leitura
    md = md.replace("TTS", "Tê-tê-êsse").replace("PT-BR", "Português do Brasil")
    md = re.sub(r"[ \t]+", " ", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()

def gen(slug: str) -> None:
    src = CONTENT / f"{slug}.md"
    text = md_to_speech(src.read_text(encoding="utf-8"))
    txt = pathlib.Path(f"/tmp/tts-{slug}.txt")
    txt.write_text(text, encoding="utf-8")
    out = STATIC / f"{slug}.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["uvx", "edge-tts", "--voice", PT_VOICE, "--rate", RATE,
         "--file", str(txt), "--write-media", str(out)],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[ERRO] {slug}: {r.stderr[-300:]}")
        sys.exit(1)
    kb = out.stat().st_size // 1024
    print(f"[OK] {out} (~{kb} KB, voz {PT_VOICE}, taxa {RATE})")

if __name__ == "__main__":
    slugs = sys.argv[1:] or [p.stem for p in sorted(CONTENT.glob("*.md"))]
    print("Gerando:", ", ".join(slugs))
    for s in slugs:
        gen(s)
