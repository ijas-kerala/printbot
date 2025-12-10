
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("1. Checking Environment Variables...")
    from core.config import settings
    # Print loaded settings (masking secrets)
    print(f"   PROJECT_NAME: {settings.PROJECT_NAME}")
    print(f"   CLOUDFLARE_TUNNEL_TOKEN: {'*' * 5 if settings.CLOUDFLARE_TUNNEL_TOKEN else 'MISSING/EMPTY'}")
    
    print("\n2. Initializing Database...")
    from core.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("   Database connection successful (SQLite).")
    
    print("\n3. Initializing FastAPI App...")
    from web.main import app
    print("   FastAPI app initialized successfully.")
    
    print("\n✅ STARTUP CHECK PASSED")
    
except Exception as e:
    print(f"\n❌ STARTUP CHECK FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
