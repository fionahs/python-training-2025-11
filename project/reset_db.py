from app.database import engine, Base
import init_db

if __name__ == "__main__":
    print("!!!" * 20)
    print("WARNING: DROPPING ALL TABLES AND ROLLING BACK MIGRATIONS")
    print("!!!" * 20)
    
    # 1. Drop everything (Clean Slate)
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped successfully.")
    
    # 2. Run standard initialization
    print("\nStarting clean initialization...")
    init_db.main()
