from app.db.database import engine, Base
from sqlalchemy import text
import app.main

with engine.connect() as conn:
    conn.execute(text('DROP SCHEMA public CASCADE;'))
    conn.execute(text('CREATE SCHEMA public;'))
    conn.commit()

Base.metadata.create_all(bind=engine)
print("Database schema reset successfully!")
