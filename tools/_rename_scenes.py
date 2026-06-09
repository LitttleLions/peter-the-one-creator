"""Rename scene files from NNN-scene-XX.md to NNN-scene-XX-ru.md."""
from pathlib import Path

ch = Path(r"c:\code\peter-the-one\output\Peter I\chapters")
for f in sorted(ch.glob("*-scene-*.md")):
    n = f.name
    # Skip already renamed files or DE translations
    if n.endswith("-de-stylized.md") or n.endswith("-de-literal.md") or n.endswith("-de-middle.md"):
        continue
    if "-ru.md" in n:
        continue
    
    new_name = f.stem + "-ru.md"
    new_path = ch / new_name
    if not new_path.exists():
        f.rename(new_path)
        print(f"{n} -> {new_name}")
print("Fertig.")