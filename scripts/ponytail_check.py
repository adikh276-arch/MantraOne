import re
import yaml
from pathlib import Path
import sys

def main():
    config_path = Path("ponytail.config.yml")
    if not config_path.exists():
        print("Missing ponytail.config.yml")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    errors = 0
    for rule_name, rule in config.get('rules', {}).items():
        pattern = rule.get('pattern')
        if not pattern:
            continue
        
        # very simple mock validation
        regex = re.compile(pattern)
        allowed = rule.get('allowed_files', [])
        target_files = rule.get('files', [])
        
        if not target_files:
            # check all .py
            files_to_check = Path(".").rglob("*.py")
        else:
            files_to_check = []
            for t in target_files:
                if "**" in t or "*" in t:
                    files_to_check.extend(Path(".").glob(t))
                else:
                    files_to_check.append(Path(t))
                    
        for pyfile in files_to_check:
            if not pyfile.exists() or pyfile.is_dir() or str(pyfile).startswith("venv") or str(pyfile).startswith(".venv"):
                continue
            str_path = str(pyfile).replace('\\', '/')
            if allowed and any(a in str_path for a in allowed):
                continue
            
            content = pyfile.read_text(encoding="utf-8", errors="ignore")
            if regex.search(content):
                print(f"[Ponytail {rule.get('severity', 'error').upper()}] {rule_name} violated in {str_path}: {rule.get('description')}")
                if rule.get('severity') == 'error':
                    errors += 1

    if errors > 0:
        print(f"Failed with {errors} errors.")
        sys.exit(1)
    print("Ponytail architecture validation passed.")

if __name__ == "__main__":
    main()
