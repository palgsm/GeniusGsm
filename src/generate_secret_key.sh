#!/bin/bash
# Generate a secure Django SECRET_KEY for production

echo "🔐 Generating Production Django SECRET_KEY..."
SECRET_KEY=$(python3 << 'EOF'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
EOF
)

echo ""
echo "Generated SECRET_KEY:"
echo "$SECRET_KEY"
echo ""
echo "Add this to your production environment (.env or deployment config):"
echo "export SECRET_KEY='$SECRET_KEY'"
echo ""
echo "✓ Never commit this key to version control"
echo "✓ Keep it secure and private"
echo "✓ If compromised, regenerate immediately"
