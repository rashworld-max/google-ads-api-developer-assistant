import os
import sys
import subprocess
import json


def get_version(ext_version_script):
    """Retrieves the extension version."""
    try:
        result = subprocess.run(
            [sys.executable, ext_version_script],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting extension version: {e}", file=sys.stderr)
        return "666"  # Fallback


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    ext_version_script = os.path.join(
        project_root, ".gemini/skills/ext_version/scripts/get_extension_version.py"
    )

    version = get_version(ext_version_script)

    new_command = f'export gaada="{version}"' 
        
    # Return the modified command to the CLI
    response = {
            "decision": "allow",
            "tool_input": {
                "command": new_command
            }
        }

    # 5. Output the final JSON to stdout
    print(json.dumps(response))

    output = {"environment": {"gaada": version}}

    # Output JSON to stdout so the CLI can consume the exported environment variables
    print(json.dumps(output))


if __name__ == "__main__":
    main()
