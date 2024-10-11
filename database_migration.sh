# Initialize migrations folder
flask db init

# Create an initial migration
flask db migrate -m "Initial migration"

# Apply migrations to the database
flask db upgrade
