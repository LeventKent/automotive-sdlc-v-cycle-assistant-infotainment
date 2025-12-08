# Resource Organization

This directory contains both **generic automotive resources** (reusable across Android Auto apps) and **weather-specific resources**.

## Naming Conventions

### Generic Automotive Resources (Reusable)
Prefix: `car_*`

These resources follow Android Automotive OS (AAOS) guidelines and can be extracted into a shared library module when building additional Android Auto apps.

**Drawables:**
- `car_button_background.xml` - Generic button with press/focus states
- `car_card_background.xml` - Generic card background
- `automotive_gradient_background.xml` - Generic dark gradient background

**Colors:**
- `car_background` - Primary background color
- `car_card_background` - Card background color
- `car_text_primary` - Primary text color (high contrast)
- `car_text_secondary` - Secondary text color
- `car_accent` - Accent color for highlights
- `car_error` - Error state color
- `car_button_primary` - Button background color
- `car_button_border` - Button border color

**Dimensions:**
- `car_touch_target_min` - 76dp (AAOS minimum)
- `car_touch_target_practical` - 64dp (practical minimum)
- `car_padding` - Standard padding (24dp)
- `car_padding_small` - Small padding (8dp)
- `car_padding_large` - Large padding (32dp)
- `car_card_radius` - Card corner radius (16dp)
- `car_button_radius` - Button corner radius (12dp)
- `car_text_*` - Typography scale (16sp - 48sp)

**Strings:**
- `car_loading` - Generic loading message
- `car_error_generic` - Generic error message
- `car_error_network` - Network error message
- `car_error_location` - Location error message

### Weather App Specific Resources
Prefix: `weather_*` or app-specific names

**Drawables:**
- `weather_refresh_button_background.xml` - Refresh button styling
- `ic_launcher_*` - App launcher icons

**Colors:**
- `weather_launcher_background` - Launcher icon background

**Strings:**
- `app_name` - Application name
- `weather_loading` - Weather-specific loading message
- `weather_error_api` - Weather API error message
- `weather_refresh` - Refresh button text

**Layouts:**
- `activity_main.xml` - Weather app main screen

## Future Extraction

When creating additional Android Auto apps, extract the `car_*` resources into a shared library module:

```
common-ui/
├── res/
│   ├── drawable/
│   │   ├── car_button_background.xml
│   │   ├── car_card_background.xml
│   │   └── automotive_gradient_background.xml
│   └── values/
│       ├── car_colors.xml
│       ├── car_dimens.xml
│       └── car_strings.xml
```

Then add as a dependency:
```kotlin
dependencies {
    implementation(project(":common-ui"))
}
```
