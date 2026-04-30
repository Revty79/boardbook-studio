from app.db.session import SessionLocal
from app.seed import seed_demo_data


if __name__ == "__main__":
    with SessionLocal() as db:
        seed_demo_data(db)
    print("Demo data seeded (if empty).")
