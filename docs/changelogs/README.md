# Changelog Documentation

This directory contains the changelog system for the Telegram Bot v3 project.

## Structure

- **Daily Changelogs**: `YYYY-MM-DD/` - Directories containing changelog entries for specific dates
- **Legacy Changelog**: `CHANGELOG_LEGACY.md` - The previous monolithic changelog file (archived)

## Date-Based Organization

Each day's changes are documented in separate directories organized by date (YYYY-MM-DD format). Within each date directory, you'll find:

- `changelog.md` - The changelog entries for that specific date
- Additional files as needed for documentation

## Usage

The changelog generator agent automatically:
1. Detects the current date
2. Creates the appropriate date directory if it doesn't exist
3. Updates or creates the changelog.md file for that date
4. Maintains chronological order with latest dates first

## Viewing Recent Changes

To see the most recent changes, look for the latest date directories. The system automatically organizes them with the most recent dates appearing first in directory listings.

## Legacy Data

All previous changelog entries have been preserved in `CHANGELOG_LEGACY.md` for historical reference.