import sys
import re

with open("models.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add TypeDecorator import
content = content.replace(
    "from sqlalchemy import (",
    "from sqlalchemy.types import TypeDecorator\nfrom sqlalchemy import ("
)

# 2. Add AwareDateTime class after _utcnow
aware_datetime_code = """
class AwareDateTime(TypeDecorator):
    \"\"\"
    A SQLAlchemy TypeDecorator that ensures DateTime objects are timezone-aware.
    SQLite natively strips timezone info on save and returns naive datetimes.
    This intercepts reads/writes and forces timezone.utc.
    \"\"\"
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

"""
content = content.replace(
    "def _utcnow() -> datetime:\n    \"\"\"Return the current UTC time (timezone-aware).\"\"\"\n    return datetime.now(timezone.utc)\n\n\n# ---------------------------------------------------------------------------",
    f"def _utcnow() -> datetime:\n    \"\"\"Return the current UTC time (timezone-aware).\"\"\"\n    return datetime.now(timezone.utc)\n{aware_datetime_code}\n# ---------------------------------------------------------------------------"
)

# 3. Replace Column(DateTime) with Column(AwareDateTime)
content = re.sub(r'Column\(DateTime(\s*[,)])', r'Column(AwareDateTime\1', content)

with open("models.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated models.py")
