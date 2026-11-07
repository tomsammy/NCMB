css_path = r'C:\Users\hp\Desktop\NCMB\static\css\style.css'

with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace root colors
css = css.replace('--primary: #004d40;', '--primary: #00563F;')
css = css.replace('--primary-light: #00796b;', '--primary-light: #007A58;')
css = css.replace('--primary-dark: #00251a;', '--primary-dark: #003627;')
css = css.replace('--primary-soft: #e0f2f1;', '--primary-soft: #E8F5E9;')
css = css.replace('--accent: #ffb300;', '--accent: #E5A823;')
css = css.replace('--accent-hover: #ffa000;', '--accent-hover: #D09314;')
css = css.replace('--accent-gold: #d97706;', '--accent-gold: #C69214;')
css = css.replace('--bg-gradient-start: #f0fdf4;', '--bg-gradient-start: #F4FBF7;')
css = css.replace('--bg-gradient-end: #e0f2f1;', '--bg-gradient-end: #E8F5E9;')

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("Updated style.css with NCDMB colors!")
