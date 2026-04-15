#!/usr/bin/env bash
# ══════════════════════════════════════════════════════
#  CampusDate — Quick Setup Script
#  Run this once to install dependencies and initialize.
# ══════════════════════════════════════════════════════
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  💕  CampusDate Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Create virtual environment
echo ""
echo "▶ Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
echo ""
echo "▶ Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt

# 3. Run migrations
echo ""
echo "▶ Running database migrations..."
python manage.py migrate

# 4. Create superuser (optional)
echo ""
echo "▶ Create an admin superuser? (y/n)"
read -r CREATE_SUPER
if [ "$CREATE_SUPER" = "y" ] || [ "$CREATE_SUPER" = "Y" ]; then
  python manage.py createsuperuser
fi

# 5. Done
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Setup complete!"
echo ""
echo "  Start the server:"
echo "    source venv/bin/activate"
echo "    python manage.py runserver"
echo ""
echo "  Then open: http://127.0.0.1:8000"
echo "  Admin:     http://127.0.0.1:8000/admin/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
