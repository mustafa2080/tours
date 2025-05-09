#!/bin/bash

set -e

# Apply database migrations with special handling for problematic migrations
echo "Applying database migrations..."

# Check if we need to rebuild the database
if [ "$REBUILD_DB" = "true" ]; then
    echo "Rebuilding database from scratch..."

    # Fake all migrations as applied
    python manage.py migrate --fake core zero

    # Then apply all migrations
    python manage.py migrate
else
    # Normal migration path with special handling for problematic migrations

    # First, fake the problematic migration
    echo "Faking problematic migrations..."
    python manage.py migrate core 0006_fix_migration --fake

    # Then fake the next migration that causes the duplicate column issue
    echo "Faking migration with duplicate column..."
    python manage.py migrate core 0007_rename_message_nl_contactmessage_message_de_and_more --fake

    # Apply the fix migration
    echo "Applying fix migration..."
    python manage.py migrate core 0008_fix_duplicate_columns --fake

    # Finally, run the rest of the migrations normally
    echo "Applying remaining migrations..."
    python manage.py migrate
fi

# Start server
echo "Starting server..."
exec "$@"
