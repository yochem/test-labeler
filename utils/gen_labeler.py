# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ruamel-yaml>=0.19.1",
# ]
# ///

"""
Generate .github/labeler.yml.

Reads the existing config and syncs team:<team-name> rules with the directories
found under environment/*/<team-name>, leaving the env:<name> rules (and any
other existing entries) untouched. Adds missing team labels, prunes stale ones,
and separates each team entry with a blank line.
"""

from pathlib import Path

from ruamel.yaml import YAML


def team_rule(team: str) -> list:
    """Build the changed-files rule for one team label."""
    return [{"changed-files": [{"any-glob-to-any-file": f"environment/*/{team}/**"}]}]


root = Path(__file__).resolve().parent.parent
config_path = root / ".github/labeler.yml"

yaml = YAML()
config = yaml.load(config_path)

# Trailing slash makes sure only directories (the team dirs) are returned
teams = sorted({team_dir.name for team_dir in root.glob("environment/*/*/")})
wanted = {f"team:{team}" for team in teams}

# Prune stale team labels
stale_teams = [k for k in config if k.startswith("team:") and k not in wanted]
for label in stale_teams:
    del config[label]

for team in teams:
    label = f"team:{team}"
    config[label] = team_rule(team)

yaml.dump(config, config_path)
