#!/bin/sh
# Link every skill folder in ~/skills into each agent's skills directory.
# Safe to re-run: existing links are left alone, real folders are never touched,
# and broken links that point into ~/skills (deleted/renamed skills) are removed.

SRC="$HOME/skills"
TARGETS="$HOME/.claude/skills $HOME/.codex/skills"
SKIP="synced"

for target in $TARGETS; do
  mkdir -p "$target"

  # Remove dead links that pointed into ~/skills
  for link in "$target"/*; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
      "$SRC"/*) [ -e "$link" ] || { rm "$link"; echo "removed dead link: $link"; } ;;
    esac
  done

  # Add links for any skill not yet present
  for dir in "$SRC"/*/; do
    name=$(basename "$dir")
    case " $SKIP " in *" $name "*) continue ;; esac
    [ -f "$dir/SKILL.md" ] || continue
    dest="$target/$name"
    if [ -L "$dest" ]; then
      continue
    elif [ -e "$dest" ]; then
      echo "skipped (real folder exists, not overwriting): $dest"
    else
      ln -s "$SRC/$name" "$dest" && echo "linked: $dest"
    fi
  done
done
