import pathlib
import tomllib
import sys

def main():
    commands_dir = pathlib.Path(".gemini/commands")
    
    if not commands_dir.exists():
        print(f"Directory not found: {commands_dir.absolute()}")
        sys.exit(1)

    files = sorted(commands_dir.glob("*.toml"))
    
    if not files:
        print("No .toml files found in .gemini/commands")
        return

    # Collect all commands and descriptions
    commands = []
    for file_path in files:
        try:
            with file_path.open("rb") as f:
                data = tomllib.load(f)
                description = data.get("description", "No description found")
                commands.append((file_path.stem, description))
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}", file=sys.stderr)

    if not commands:
        return

    # Calculate max length for alignment
    max_len = max(len(cmd[0]) for cmd in commands)
    
    # Print aligned output
    # We add a few spaces gap between command and description
    gap = 3
    for name, description in commands:
        print(f"{name:<{max_len + gap}}{description}")

if __name__ == "__main__":
    main()
