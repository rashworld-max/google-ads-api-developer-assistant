#!/bin/bash
set -u

# Setup environment
TEST_DIR=$(mktemp -d)
cd "${TEST_DIR}"

mkdir .gemini
SETTINGS_JSON=".gemini/settings.json"

# function to mimic err
err() {
    echo "ERROR: $*" >&2
}

# Create "user" settings (simulating existing file)
echo '{"user_setting": true, "common_setting": "user_value"}' > "${SETTINGS_JSON}"

# Define the logic block to test (extracted from update.sh)
run_update_logic() {
    SETTINGS_JSON=".gemini/settings.json"
    TEMP_SETTINGS=$(mktemp)

    # 1. Backup existing settings if they exist
    if [[ -f "${SETTINGS_JSON}" ]]; then
        echo "Backing up ${SETTINGS_JSON}..."
        cp "${SETTINGS_JSON}" "${TEMP_SETTINGS}"
        
        # MOCK: git checkout would go here
        echo "Mocking git checkout..."
    fi

    # MOCK: git pull (simulating update that changes settings.json)
    echo "Mocking git pull (updating settings.json)..."
    # Overwrite settings.json with "repo" version
    echo '{"repo_setting": true, "common_setting": "repo_value"}' > "${SETTINGS_JSON}"

    # 3. Restore/Merge settings
    if [[ -f "${TEMP_SETTINGS}" ]] && [[ -s "${TEMP_SETTINGS}" ]]; then
        echo "Merging preserved settings with new defaults..."
        if jq -s '.[0] * .[1]' "${SETTINGS_JSON}" "${TEMP_SETTINGS}" > "${TEMP_SETTINGS}.merged"; then
            mv "${TEMP_SETTINGS}.merged" "${SETTINGS_JSON}"
            echo "Settings restored and merged successfully."
        else
            echo "WARN: Failed to merge settings.json."
        fi
        rm -f "${TEMP_SETTINGS}"
    fi
}

echo "Initial settings:"
cat "${SETTINGS_JSON}"

run_update_logic

echo "Final settings:"
cat "${SETTINGS_JSON}"

# Verify
USER_VAL=$(jq -r .user_setting "${SETTINGS_JSON}")
REPO_VAL=$(jq -r .repo_setting "${SETTINGS_JSON}")
COMMON_VAL=$(jq -r .common_setting "${SETTINGS_JSON}")

if [[ "$USER_VAL" == "true" ]] && [[ "$REPO_VAL" == "true" ]] && [[ "$COMMON_VAL" == "user_value" ]]; then
    echo "TEST PASSED"
else
    echo "TEST FAILED"
    echo "user_setting: $USER_VAL (expected true)"
    echo "repo_setting: $REPO_VAL (expected true)"
    echo "common_setting: $COMMON_VAL (expected user_value)"
    exit 1
fi
