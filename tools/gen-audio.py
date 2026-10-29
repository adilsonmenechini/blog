#!/usr/bin/env python3
"""Gera audiobook dos artigos do blog (Edge TTS).
Uso: python3 tools/gen-audio.py [pt|en] [slug ...]   # sem args = pt + todos os posts
"""
import pathlib, re, subprocess, sys, html

VOICE = {"pt": "pt-BR-AntonioNeural", "en": "en-US-AndrewNeural", "es": "es-ES-AlvaroNeural"}
RATE = "+0%"

def md_to_speech(md: str, lang: str) -> str:
    cue = "[Trecho de código exibido no artigo.]" if lang == "pt" else "[Code snippet shown in the article.]"
    # remove frontmatter
    md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)
    # remove hugo shortcodes
    md = re.sub(r"\{\{[%<].*?[%>]\}\}", "", md)
    md = re.sub(r"```[a-z]*\n.*?\n```", f" {cue} ", md, flags=re.S)
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

def gen(lang: str, slug: str) -> None:
    content = pathlib.Path(f"content/{lang}/posts")
    src = content / f"{slug}.md"
    text = md_to_speech(src.read_text(encoding="utf-8"), lang)
    static = pathlib.Path(f"static/audio/{lang}")
    txt = pathlib.Path(f"/tmp/tts-{lang}-{slug}.txt")
    txt.write_text(text, encoding="utf-8")
    out = static / f"{slug}.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    voice = VOICE[lang]
    r = subprocess.run(
        ["uvx", "edge-tts", "--voice", voice, "--rate", RATE,
         "--file", str(txt), "--write-media", str(out)],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[ERRO] {slug}: {r.stderr[-300:]}")
        sys.exit(1)
    kb = out.stat().st_size // 1024
    print(f"[OK] {out} (~{kb} KB, voz {voice}, taxa {RATE})")

if __name__ == "__main__":
    args = sys.argv[1:]
    lang = "pt"
    if args and args[0] in VOICE:
        lang = args.pop(0)
    slug_args = args or [p.stem for p in sorted(pathlib.Path(f"content/{lang}/posts").glob("*.md"))
                         if p.stem != "_index"]
    print(f"Idioma {lang}: gerando", ", ".join(slug_args))
    for s in slug_args:
        gen(lang, s)
