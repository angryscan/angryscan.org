# Download Page Configuration

## Overview

The download page generation system is split into two files:
- `download_config.yaml` - configuration rules and settings in YAML format
- `generate_downloads_page.py` - main generation script

## Configuration Structure

### YAML Structure

The configuration is organized into the following sections:

```yaml
# Page settings
page:
  title: "Download"
  description: "Page description"
  subtitle: "Subtitle"

# Repository settings
repository:
  owner: "angryscan"
  name: "angrydata-app"

# Operating systems display order
os_order:
  - "Windows"
  - "Linux"
  - "MacOS"

# Operating systems configuration
operating_systems:
  Windows:
    label: "🪟 **Windows**"
    icon: "windows"
    color_scheme:
      primary: "#0078d6"
      secondary: "#00bcf2"

# Asset rules
asset_rules:
  - os_name: "Windows"
    display_name: "Windows"
    description: "Download for Windows"
    badge_url: "https://img.shields.io/badge/Setup-x64-0078D6?style=for-the-badge&logo=windows"
    alt_text: "Windows setup (x64)"
    suffixes:
      - ".exe"
    preferred_substrings:
      - "amd64"
      - "x64"
```

### Adding New Asset Types

1. **Add a new rule to `asset_rules`**:
```yaml
asset_rules:
  - os_name: "Windows"
    display_name: "Windows ARM"
    description: "Download for Windows ARM"
    badge_url: "https://img.shields.io/badge/ARM-64-0078D6?style=for-the-badge&logo=windows"
    alt_text: "Windows ARM build"
    suffixes:
      - "-arm64.exe"
      - "-aarch64.exe"
    preferred_substrings:
      - "arm64"
      - "aarch64"
```

2. **Update OS configuration if needed**:
```yaml
operating_systems:
  Android:
    label: "🤖 **Android**"
    placeholder: "N/A"
    icon: "android"
    color_senses:
      primary: "#3DDC84"
      secondary: "#2E7D32"
```

3. **Add OS to display order**:
```yaml
os_order:
  - "Windows"
  - "Linux"
  - "macOS"
  - "Android"
```

### Styling Configuration

Styles are located in the `render_css_styles()` function in the main script. To modify:

1. **Brand colors** - change CSS variables
2. **Animations** - configure `transition` properties
3. **Responsiveness** - update media queries

### Page Structure

The page consists of:
1. **Header** - title and description
2. **Release information** - version and date
3. **Download cards** - one for each OS
4. **Release link** - full release notes
5. **Tip** - auto-update information

## YAML Configuration Benefits

### Readability
- Human-readable format
- Easy to edit without Python knowledge
- Comments are supported

### Easy Editing
- No need to know Python syntax
- Syntax validation in editors
- Autocomplete in modern IDEs

### Flexibility
- Easy to add new fields
- Support for multi-level structures
- Ability to use variables

## Extending Functionality

### Adding New File Types

1. Define rules in `download_config.yaml`
2. Add corresponding CSS styles to the main script
3. Update file selection logic if needed

### Customizing Display

1. Modify `render_download_card()` for new card structure
2. Update `render_css_styles()` for new styles
3. Modify `format_release()` to change layout

### Supporting New Platforms

1. Add OS to `os_order` in YAML
2. Create configuration in `operating_systems`
3. Define asset rules for the new platform
4. Add corresponding CSS styles
