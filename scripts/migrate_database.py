#!/usr/bin/env python3
"""
Database migration script to add status and error_message fields to existing databases.

Usage:
    python migrate_database.py

This script will:
1. Add 'status' column with default value 'uploaded'
2. Add 'error_message' column (nullable)
3. Update existing documents to have 'processed' status if they have content
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def migrate_database():
    """Add new columns to documents table"""
    from database import SessionLocal, engine
    from sqlalchemy import text
    
    print("🔄 Starting database migration...")
    
    db = SessionLocal()
    
    try:
        # Check if columns already exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='documents'
        """))
        columns = [row[0] for row in result]
        
        has_status = 'status' in columns
        has_error_message = 'error_message' in columns
        
        if has_status and has_error_message:
            print("✅ Database already has status and error_message columns")
            return True
        
        # Add status column if not exists
        if not has_status:
            print("Adding 'status' column...")
            try:
                db.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN status VARCHAR DEFAULT 'uploaded'
                """))
                db.commit()
                print("✅ Added 'status' column")
            except Exception as e:
                print(f"Note: {e}")
                # Column might already exist in SQLite (different error handling)
                db.rollback()
        
        # Add error_message column if not exists
        if not has_error_message:
            print("Adding 'error_message' column...")
            try:
                db.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN error_message TEXT
                """))
                db.commit()
                print("✅ Added 'error_message' column")
            except Exception as e:
                print(f"Note: {e}")
                db.rollback()
        
        # Update existing documents
        print("Updating existing documents...")
        db.execute(text("""
            UPDATE documents 
            SET status = CASE 
                WHEN content IS NOT NULL AND content != '' THEN 'processed'
                ELSE 'uploaded'
            END
            WHERE status IS NULL OR status = ''
        """))
        db.commit()
        print("✅ Updated existing documents with status")
        
        print("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def migrate_sqlite():
    """Migration for SQLite databases (simpler approach)"""
    from database import SessionLocal, engine, Base
    from models import Document
    
    print("🔄 Running SQLite migration...")
    
    try:
        # Recreate tables - SQLite doesn't support ALTER COLUMN easily
        print("Creating/updating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Update existing documents
        db = SessionLocal()
        try:
            documents = db.query(Document).all()
            for doc in documents:
                if not doc.status:
                    if doc.content:
                        doc.status = 'processed'
                    else:
                        doc.status = 'uploaded'
            db.commit()
            print(f"✅ Updated {len(documents)} existing documents")
        finally:
            db.close()
        
        print("🎉 SQLite migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("📋 Database Migration for File Upload Improvements")
    print("=" * 60)
    
    # Determine database type from DATABASE_URL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./dartos.db')
    
    if database_url.startswith('sqlite'):
        print("Detected SQLite database")
        success = migrate_sqlite()
    else:
        print("Detected PostgreSQL/other database")
        success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your backend server")
        print("2. Test file upload and status tracking")
        return 0
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        print("\nYou can also manually add the columns:")
        print("  ALTER TABLE documents ADD COLUMN status VARCHAR DEFAULT 'uploaded';")
        print("  ALTER TABLE documents ADD COLUMN error_message TEXT;")
        return 1

if __name__ == "__main__":
    sys.exit(main())
