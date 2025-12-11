# Database Migrations & Best Practices

## Information for Users

If you encounter `sqlite3.OperationalError: no such column: ...`, it means the database file (`printbot.db`) has an older schema than what the code expects. This often happens during development when models are updated but the database file is preserved.

### How to Fix
We have provided a utility script to auto-fix common schema issues.
Run the following command in the project root:

```bash
python3 scripts/fix_db_schema.py
```

This script checks for missing columns like `total_pages` and `page_range` and adds them safely.

## For Developers: Schema Management

### Current Approach (Simple)
We currently use a manual migration script (`scripts/fix_db_schema.py`) to patch the SQLite database on startup or on demand. This is suitable for simple prototypes.

### Recommended Approach (Production)
For a robust production environment, we verify strongly recommend using **Alembic** for database migrations.

#### 1. Setup Alembic
```bash
pip install alembic
alembic init alembic
```

#### 2. Configure Alembic
Edit `alembic.ini` to point to `sqlalchemy.url = sqlite:///./printbot.db`.
Edit `alembic/env.py` to import your models:
```python
from web.models.models import Base
target_metadata = Base.metadata
```

#### 3. Create Migrations
Whenever you modify `models.py`, generate a migration script:
```bash
alembic revision --autogenerate -m "Added page_range column"
```

#### 4. Apply Migrations
```bash
alembic upgrade head
```

This ensures all database changes are tracked, reversible, and consistent across environments.
