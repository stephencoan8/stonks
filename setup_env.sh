# Create .env from example
cp .env.example .env

# Generate a secure secret key
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
echo "SECRET_KEY=$SECRET_KEY" > .env

echo "FLASK_ENV=development" >> .env
echo "FLASK_APP=main.py" >> .env
echo "DATABASE_URL=sqlite:///stonks.db" >> .env
echo "ADMIN_USERNAME=admin" >> .env
echo "ADMIN_PASSWORD=admin" >> .env

echo ".env file created!"
