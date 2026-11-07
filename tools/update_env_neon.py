neon_url = "postgresql://neondb_owner:npg_7qXbkc2RIhPC@ep-shy-breeze-bbue2qt8-pooler.c-15.us-east-1.aws.neon.tech/neondb?sslmode=require"

for p in [r"C:\Users\hp\Desktop\NCMB\.env", r"C:\Users\hp\Desktop\NCMB\.env.example"]:
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    import re
    content = re.sub(r'DATABASE_URL=".*?"', f'DATABASE_URL="{neon_url}"', content)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {p} with Neon DATABASE_URL")
