@echo off
python renderer.py > output.md
pandoc --from=markdown output.md --include-in-header=extra.html -s > output.html