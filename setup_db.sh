#!/bin/bash
echo "Reverting to original configuration..."

# 1. Drop the temporary user if it exists
echo "Dropping user 'flight_user'..."
sudo -u postgres psql -c "DROP USER IF EXISTS flight_user;"

# 2. Force 'postgres' user to have password 'postgres'
echo "Setting password for 'postgres'..."
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# 3. Ensure DB exists and is owned by postgres
echo "Configuring database 'airplane_analytics'..."
sudo -u postgres psql -c "CREATE DATABASE airplane_analytics OWNER postgres;" || sudo -u postgres psql -c "ALTER DATABASE airplane_analytics OWNER TO postgres;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE airplane_analytics TO postgres;"

echo "Done! User 'flight_user' deleted. Using 'postgres'/'postgres'."
