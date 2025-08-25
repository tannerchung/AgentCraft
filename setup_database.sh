#!/bin/bash

# AgentCraft Database Setup Script
echo "🗄️  Setting up AgentCraft PostgreSQL Database..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL not found. Please install PostgreSQL first:"
    echo "   macOS: brew install postgresql@15"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Check if PostgreSQL service is running
if ! pg_isready -h localhost -p 5432; then
    echo "❌ PostgreSQL service is not running. Please start it:"
    echo "   macOS: brew services start postgresql@15"
    echo "   Ubuntu: sudo systemctl start postgresql"
    exit 1
fi

# Prompt for database password
echo "📝 Please set a password for the 'tanner' database user:"
read -s -p "Password: " DB_PASSWORD
echo ""

# Connect as superuser and create database/user
echo "🔧 Creating database and user..."
psql -U postgres -d postgres << EOF
CREATE DATABASE agentcraft_db;
CREATE USER tanner WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE agentcraft_db TO tanner;
ALTER USER tanner WITH SUPERUSER;
EOF

if [ $? -ne 0 ]; then
    echo "⚠️  Failed to connect as 'postgres' user. Trying default user..."
    psql -d postgres << EOF
CREATE DATABASE agentcraft_db;
CREATE USER tanner WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE agentcraft_db TO tanner;
ALTER USER tanner WITH SUPERUSER;
EOF
fi

# Update .env file
echo "📝 Updating .env file with database credentials..."
sed -i.bak "s|DATABASE_URL=.*|DATABASE_URL=postgresql://tanner:$DB_PASSWORD@localhost:5432/agentcraft_db|g" .env

# Run schema
echo "🏗️  Running database schema..."
psql -d agentcraft_db -U tanner -f database/schema.sql

if [ $? -eq 0 ]; then
    echo "✅ Database setup complete!"
    echo "🚀 You can now restart your backend server to connect to the database."
    echo ""
    echo "💡 Next steps:"
    echo "   1. Stop the current backend: pkill -f 'python.*backend.main'"
    echo "   2. Start the backend: python3 -m backend.main"
    echo "   3. Test the chat interface at http://localhost:3000"
else
    echo "❌ Schema setup failed. Please check the error messages above."
    exit 1
fi