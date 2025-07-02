# reset_users.py

from app.database import SessionLocal
from app.models import User

# Start DB session
db = SessionLocal()

# Delete all users
db.query(User).delete()

# Save and close
db.commit()
db.close()

print("✅ All users deleted from DB")
