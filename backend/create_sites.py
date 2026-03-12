import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from business.models import Site

def create_sites():
    sites = ["Nyarubuye", "Bwana", "Nkomangwa", "Home"]
    for site_name in sites:
        if not Site.objects.filter(name=site_name).exists():
            Site.objects.create(name=site_name)
            print(f"Created site: {site_name}")
        else:
            print(f"Site {site_name} already exists")

if __name__ == "__main__":
    create_sites()
