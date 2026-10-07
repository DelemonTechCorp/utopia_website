import requests
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from utopia_realty_app.models import *


class Command(BaseCommand):
    help = "Fetch ALL properties (paginated) and sync with DB"

    BASE_LIST_URL = "https://microservice.x-opp.com/api/properties/"
    BASE_DETAIL_URL = "https://microservice.x-opp.com/api/property/{}/"
    BASE_MEDIA_URL = "https://microservice.x-opp.com/"

    def handle(self, *args, **options):
        next_url = self.BASE_LIST_URL
        total_created = 0
        total_updated = 0

        api_property_ids = set()  # ✅ Track API IDs

        self.stdout.write(self.style.SUCCESS("Starting full property sync..."))

        while next_url:
            response = requests.get(next_url, timeout=120)
            response.raise_for_status()
            json_data = response.json()

            if not json_data.get("status"):
                self.stderr.write("API returned status=False")
                return

            data = json_data.get("data", {})
            results = data.get("results", [])
            next_url = data.get("next_page_url")

            for item in results:
                api_property_ids.add(item["id"])  # ✅ Collect ID

                property_obj, created = self.sync_basic_property(item)

                if created:
                    total_created += 1
                else:
                    total_updated += 1

                try:
                    self.sync_property_detail(property_obj.external_id)
                except requests.exceptions.RequestException as e:
                    self.stderr.write(
                        f"❌ Failed detail sync for Property ID {property_obj.external_id}: {str(e)}"
                    )
                    continue
                self.stdout.write(f"Synced Property ID: {item['id']}")

        # ✅ SAFETY CHECK (avoid wiping DB if API fails)
        if not api_property_ids:
            self.stderr.write("No properties fetched from API — skipping deletion for safety.")
            return

        # ✅ DELETE STALE PROPERTIES
        self.stdout.write("Cleaning up stale properties...")

        with transaction.atomic():
            deleted_count, _ = Property.objects.exclude(
                external_id__in=api_property_ids
            ).delete()

        self.stdout.write(
            self.style.WARNING(f"Deleted {deleted_count} stale properties")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSYNC COMPLETED ✅ Created: {total_created} | Updated: {total_updated}"
            )
        )

    def normalize_media_url(self, path):
        if not path:
            return None
        if path.startswith("http"):
            return path
        return self.BASE_MEDIA_URL + path.lstrip("/")

    def sync_basic_property(self, item):
        with transaction.atomic():

            # Developer
            dev_data = item.get("developer")

            if dev_data:
                dev_slug = dev_data.get("slug") or slugify(
                    dev_data.get("name", f"dev-{dev_data.get('id', 0)}")
                )

                developer_obj, _ = Developer.objects.update_or_create(
                    slug=dev_slug,
                    defaults={
                        "name": dev_data.get("name", "Unknown Developer"),
                        "logo": self.normalize_media_url(dev_data.get("logo")),
                        "website": dev_data.get("website"),
                        "email": dev_data.get("email"),
                        "phone": dev_data.get("phone"),
                        "address": dev_data.get("address"),
                        "overview": dev_data.get("overview"),
                    },
                )
            else:
                developer_obj, _ = Developer.objects.get_or_create(
                    slug="unknown-developer",
                    defaults={"name": "Unknown Developer"},
                )

            # City
            city_data = item.get("city")
            if city_data:
                city_name_en = city_data["name"]["en"]
                city_slug = slugify(city_data["name"]["en"])
            else:
                city_slug = "city-unknown"
                city_name_en = "Unknown City"

            city, _ = City.objects.get_or_create(
                slug=city_slug,
                defaults={"name": city_name_en},
            )

            # District
            district_data = item.get("district")
            district_id = district_data.get("id") if district_data else None
            district_name_en = (
                district_data["name"]["en"] if district_data else "Unknown District"
            )

            if district_id:
                district, _ = District.objects.get_or_create(
                    id=district_id,
                    defaults={"name": district_name_en, "city": city},
                )
            else:
                district, _ = District.objects.get_or_create(
                    name=district_name_en,
                    city=city,
                )

            # Property Status
            ps_id = str(item.get("property_status"))
            PROPERTY_STATUS_MAP = {
                "1": (1, "Ready"),
                "2": (2, "Off Plan"),
            }

            id, ps_name = PROPERTY_STATUS_MAP.get(
                ps_id, (int(ps_id), f"Status {ps_id}")
            )

            property_status, _ = PropertyStatus.objects.update_or_create(
                id=id,
                defaults={"name": ps_name},
            )

            # Sales Status
            ss_data = item.get("sales_status")

            SALES_STATUS_MAP = {
                "1": "Available",
                "2": "Pre Launch",
                "4": "Sold Out",
                "5": "Price On Demand",
            }

            if isinstance(ss_data, dict):
                ss_name = ss_data.get("name") or "Unknown Status"
            else:
                ss_name = SALES_STATUS_MAP.get(str(ss_data), f"Sales {ss_data}")

            sales_status, _ = SalesStatus.objects.update_or_create(name=ss_name)

            # Property Type
            ptype_data = item.get("property_type")

            if isinstance(ptype_data, dict):
                ptype_name = ptype_data.get("name")
            else:
                if str(ptype_data) == "3":
                    ptype_name = "Commercial"
                elif str(ptype_data) == "20":
                    ptype_name = "Residential"
                else:
                    ptype_name = f"Type {ptype_data}"

            property_type, _ = PropertyType.objects.update_or_create(
                name=ptype_name,
            )

            # Delivery Date
            raw_date = str(item.get("delivery_date"))
            if raw_date and len(raw_date) == 6:
                delivery_date = date(int(raw_date[:4]), int(raw_date[4:]), 1)
            else:
                delivery_date = date(1970, 1, 1)

            # Slug
            property_slug = slugify(
                f"{district.name}-{city.name}-{item['title']['en']}"
            )

            # Create / Update
            property_obj, created = Property.objects.update_or_create(
                external_id=item["id"],
                defaults={
                    "title": item["title"]["en"],
                    "slug": property_slug,
                    "cover": item.get("cover"),
                    "address": item.get("address") or "",
                    "address_text": item.get("address_text") or "",
                    "delivery_date": delivery_date,
                    "low_price": item.get("low_price") or 0,
                    "min_area": item.get("min_area") or 0,
                    "property_status": property_status,
                    "sales_status": sales_status,
                    "developer": developer_obj,
                    "city": city,
                    "district": district,
                    "property_type": property_type,
                },
            )

            return property_obj, created

    def sync_property_detail(self, property_id):
        url = self.BASE_DETAIL_URL.format(property_id)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json().get("data")

        with transaction.atomic():
            property_obj = Property.objects.filter(
                external_id=data["id"]
            ).first()

            if not property_obj:
                return

            property_obj.description = data["description"]["en"]
            property_obj.residential_units = data.get("residential_units", 0)
            property_obj.commercial_units = data.get("commercial_units", 0)
            property_obj.completion_rate = data.get("completion_rate", 0)
            property_obj.last_synced_at = timezone.now()
            property_obj.save()

            PropertyImages.objects.filter(property=property_obj).delete()

            for img in data.get("property_images", []):
                image_path = img.get("image")
                if image_path and not image_path.startswith("http"):
                    image_path = self.BASE_MEDIA_URL + image_path.lstrip("/")

                PropertyImages.objects.create(
                    property=property_obj,
                    image=image_path,
                )

            property_obj.facilities.clear()

            for facility in data.get("facilities", []):
                facility_obj, _ = Facility.objects.get_or_create(
                    name=facility["name"]["en"],
                )
                property_obj.facilities.add(facility_obj)

            GroupedApartment.objects.filter(property=property_obj).delete()

            for group in data.get("grouped_apartments", []):
                unit_type = group.get("unit_type", {}).get("en")
                rooms_data = group.get("rooms", {}).get("en", "")

                if not unit_type:
                    continue

                if rooms_data.lower() == "studio":
                    bedrooms = 0
                else:
                    try:
                        bedrooms = int(rooms_data.split("BR")[0])
                    except:
                        bedrooms = 0

                GroupedApartment.objects.update_or_create(
                    property=property_obj,
                    unit_type=unit_type,
                    rooms=bedrooms,
                    defaults={
                        "min_price": group.get("min_price"),
                        "min_area": group.get("min_area"),
                    },
                )