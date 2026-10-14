from pathlib import Path
import re

text = Path("manuscript/writing_kit/manuscript_rendered.md").read_text(encoding="utf-8")
text = re.sub(r"^# Draft for.*?\n---\n", "", text, count=1, flags=re.S)
m = re.search(r"## Abstract\n\n(.*?)\n\n\*\*Keywords", text, re.S)
abs_t = re.sub(r"\s+", " ", m.group(1)).strip()
print("ABSTRACT_WORDS", len(abs_t.split()))
print("ABSTRACT:", abs_t)
print()
sections = re.split(r"\n## ", text)
total = 0
for s in sections[1:]:
    title, _, body = s.partition("\n")
    words = re.findall(r"\b[\w']+\b", body)
    total += len(words)
    print("%5d  %s" % (len(words), title.strip()[:70]))
print("TOTAL", total)
