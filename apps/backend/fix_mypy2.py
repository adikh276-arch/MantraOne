import os

fixes = [
    (
        "core/repositories/base.py",
        [
            ("self.model.id == entity_id,", "getattr(self.model, 'id') == entity_id,  # type: ignore"),
            ("self.model.family_id == family_id,", "getattr(self.model, 'family_id') == family_id,  # type: ignore"),
            (
                'self.model.deleted_at.is_(None) if hasattr(self.model, "deleted_at") else True,',
                'getattr(self.model, "deleted_at").is_(None) if hasattr(self.model, "deleted_at") else True,  # type: ignore',
            ),
            (
                "entity.deleted_at = datetime.now(timezone.utc)",
                "setattr(entity, 'deleted_at', datetime.now(timezone.utc))  # type: ignore",
            ),
        ],
    )
]

for file_path, replacements in fixes:
    full_path = f"d:/MantraOne/mantraone-backend/{file_path}"
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        continue
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f"Could not find '{old}' in {file_path}")

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Mypy fixes applied (base.py).")
