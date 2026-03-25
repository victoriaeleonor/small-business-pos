import sys; sys.path.insert(0, 'src')
import database as db
db.init_db()
db.save_user("Admin", "admin", "admin123")
print("User created: admin / admin123")