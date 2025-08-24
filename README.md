# Smart Updater

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

Smart Updater is a custom integration for Home Assistant that helps you manage your updates. It automatically finds available updates for your HACS components and Home Assistant Core, and allows you to update them selectively or automatically.

## Features

-   **Update Sensor:** A sensor that shows the number of available updates.
-   **Update Service:** A service to update selected components.
-   **Lovelace Card:** A custom card to view and manage updates from your dashboard.
-   **Scheduled Auto-updates:** Configure automatic updates for your components at a time of your choosing.

## Installation

1.  Copy the `smart_updater` directory from this repository into your Home Assistant's `custom_components` directory.
2.  Restart Home Assistant.
3.  Go to **Settings > Devices & Services > Add Integration** and search for **Smart Updater**.
4.  Click on the integration to add it.

## Configuration

You can configure the integration from the options menu of the integration's entry in **Settings > Devices & Services**.

-   **Auto-update time:** Set the time of day when the automatic updates should run.
-   **Auto-update entities:** Select the components you want to update automatically.

## Usage

### Lovelace Card

To use the card in your dashboard, add a new card and select the "Custom: Smart Updater Card".

```yaml
type: custom:smart-updater-card
entity: sensor.smart_updater
```

The card will display a list of available updates. You can select the ones you want to update and click the "Update Selected" button.

### Service

The integration provides a service `smart_updater.update_selected` that you can use in your automations.

**Service:** `smart_updater.update_selected`

**Data:**

| Name        | Description                      | Example                               |
|-------------|----------------------------------|---------------------------------------|
| `entity_id` | A list of update entity IDs to install. | `["update.hacs_integration", "update.home_assistant_core_update"]` |
