# National Day Setup Guide

Display today's national days and fun observances from a bundled dataset.

## Overview

The National Day plugin ships with a bundled dataset of popular national days and fun observances organized by month and day. No external API or network connection is required. The dataset covers hundreds of observances.



### Prerequisites

No API key or network connection required.

## Quick Setup

1. **Enable** — Go to **Integrations** in your FiestaBoard settings and enable **National Day**.
2. **Configure** — Fill in the plugin settings (see Configuration Reference below).
3. **Template** — Add a page using the `national_day` plugin variables:
   ```
   {{{ national_day.status }}}
   ```
4. **View** — Navigate to your board page to see the live display.

## Template Variables

| Variable | Description | Example |
|---|---|---|
| `national_day.holiday` | Name of the national day / observance | `National Coffee Day` |
| `national_day.date` | Today's date | `September 29` |
| `national_day.count` | Total number of observances today | `3` |

## Configuration Reference

| Setting | Name | Description | Default |
|---|---|---|---|
| `enabled` | Enabled |  | `False` |
| `holiday_index` | Holiday Position | Which holiday to show when there are multiple (1 = first). | `1` |
| `refresh_seconds` | Refresh Interval (seconds) | How often to refresh (once per day is sufficient). | `3600` |

## Troubleshooting

- **Missing holiday** — some dates may have no entries; add custom entries to `data/national_days.json`.

