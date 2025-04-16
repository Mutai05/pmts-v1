import csv
import os
import traceback
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.db import transaction

# Adjust these imports based on your actual app structure
try:
    from projects.models import Project
except ImportError:
    raise CommandError("Ensure 'projects' app is correctly installed and Project model exists.")
try:
    # Assuming Ward is in departments based on initial seeding info
    from departments.models import Department, Ward
except ImportError:
    # Fallback if Ward is in locations or another app
    try:
        from locations.models import Ward
        from departments.models import Department # Still need Department
    except ImportError:
        raise CommandError("Ensure 'departments' app (with Department model) and app with Ward model (e.g., 'departments' or 'locations') are correctly installed.")

class Command(BaseCommand):
    help = 'Seeds the database with project data from projects.csv for FY 2022-2023'

    def handle(self, *args, **options):
        # Define fixed values
        financial_year = "2022-2023"
        start_date = date(2022, 6, 1)
        end_date = date(2023, 5, 30)
        # Assume projects.csv is in the Django project root directory
        # Correctly navigate up from management/commands/ to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_file_path = os.path.join(project_root, 'projects.csv')

        if not os.path.exists(csv_file_path):
            raise CommandError(f"File not found: {csv_file_path}. Make sure 'projects.csv' is in the project root: {project_root}")

        # --- Mappings ---
        department_mapping = {
            "roads and infrastructure": "Public Works, Roads, Transport Infrastructure & Energy",
            "public works and energy": "Public Works, Roads, Transport Infrastructure & Energy",
            "integrated service delivery (isd) logistics": "Public Service Management & Governance",
            "executive": "Public Service Management & Governance", # Map 'Executive' department
            # Add other known mappings (lowercase keys)
        }
        # Fallback department if lookup fails but needed (e.g., non-capital with blank agency)
        default_department_name = "Public Service Management & Governance"

        status_mapping = {
            "complete": "completed",
            "complete and in use": "completed",
            "ongoing": "ongoing",
            "stalled": "stalled",
            # Add others if needed (lowercase keys)
        }

        funding_source_mapping = {
            "cgtn": "county",
            # Add others if needed (lowercase keys)
        }

        # --- Processing ---
        projects_created_count = 0
        projects_updated_count = 0
        projects_skipped_count = 0
        projects_skipped_existing = 0 # Add counter for skipped existing projects
        is_non_capital_section = False
        processed_rows = 0
        row_num = 0 # Initialize for error reporting outside loop
        project_name = "N/A" # Initialize for error reporting

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                try:
                    header = next(reader)
                except StopIteration:
                     raise CommandError(f"CSV file is empty or contains only a header: {csv_file_path}")

                # Validate header roughly (optional but recommended)
                expected_headers = ["Project Name", "Sub-County", "Ward", "Implementing Agency", "Budgeted Amount", "Project Cost"]
                if not all(h in header for h in expected_headers):
                     self.stdout.write(self.style.WARNING(f"CSV header {header} doesn't match expected columns {expected_headers} exactly. Proceeding, but check column indices and mapping."))

                with transaction.atomic(): # Use a transaction for atomicity
                    for i, row in enumerate(reader):
                        processed_rows += 1
                        row_num = i + 2 # 1-based index + header

                        # Check for empty rows or the non-capital marker
                        if not any(field.strip() for field in row):
                            self.stdout.write(self.style.NOTICE(f"Skipping empty row {row_num}"))
                            projects_skipped_count += 1
                            continue
                        if len(row) > 0 and row[0].strip().upper() == "NON CAPITAL PROJECTS":
                            is_non_capital_section = True
                            self.stdout.write(self.style.SUCCESS("\n--- Processing Non-Capital Projects section ---"))
                            continue
                        # Skip header-like rows within the data if necessary
                        if len(row) > 0 and row[0].strip().lower() == "project name":
                             self.stdout.write(self.style.NOTICE(f"Skipping likely header row {row_num}"))
                             projects_skipped_count += 1
                             continue

                        # --- Basic data extraction ---
                        try:
                            project_name = row[0].strip()
                            if not project_name:
                                self.stdout.write(self.style.WARNING(f"Skipping row {row_num}: Empty project name"))
                                projects_skipped_count += 1
                                continue

                            project_desc = row[1].strip()
                            raw_status = row[2].strip().lower()
                            # Col 3, 4 are Start/End Date - Ignored per request
                            raw_percentage = row[5].strip().replace('%', '')
                            sub_county_name_raw = row[6].strip()
                            ward_name_raw = row[7].strip()
                            # location = row[8].strip() # Not used directly in Project model
                            google_map_url = row[9].strip() if row[9].strip() else None
                            implementing_agency_raw = row[10].strip()
                            contractor = row[11].strip() if row[11].strip() else None
                            budget_raw = row[12].strip().replace(',', '')
                            expenditure_raw = row[13].strip().replace(',', '') # Often corresponds to Project Cost
                            funding_source_raw = row[14].strip().lower()
                            remarks = row[15].strip() if len(row) > 15 else ""

                        except IndexError:
                            self.stdout.write(self.style.WARNING(f"Skipping row {row_num} ('{project_name}'): Not enough columns (expected at least 16)."))
                            projects_skipped_count += 1
                            continue

                        # --- Determine Project Type ---
                        project_type = 'non_capital' if is_non_capital_section else 'capital'

                        # --- Data Cleaning and Lookup ---

                        # Department Lookup
                        department = None
                        agency_lower = implementing_agency_raw.lower()
                        department_name_mapped = department_mapping.get(agency_lower)

                        target_department_name = None
                        if department_name_mapped:
                            target_department_name = department_name_mapped
                        elif implementing_agency_raw: # Try direct match if not blank and not in explicit mapping
                            target_department_name = implementing_agency_raw
                        elif project_type == 'non_capital': # Use default for non-capital if agency is blank
                            target_department_name = default_department_name

                        if target_department_name:
                            try:
                                department = Department.objects.get(name__iexact=target_department_name)
                            except Department.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"Skipping row {row_num} ('{project_name}'): Department '{target_department_name}' (from Agency '{implementing_agency_raw}') not found."))
                                projects_skipped_count += 1
                                continue
                            except Department.MultipleObjectsReturned:
                                self.stdout.write(self.style.ERROR(f"Error row {row_num} ('{project_name}'): Multiple Departments match '{target_department_name}'. Check data integrity."))
                                projects_skipped_count += 1
                                continue
                        elif project_type == 'capital': # Capital projects must have a department
                            self.stdout.write(self.style.WARNING(f"Skipping row {row_num} ('{project_name}'): Missing Implementing Agency for capital project."))
                            projects_skipped_count += 1
                            continue
                        # If non-capital and no department found/specified, department remains None (if model allows)
                        # Current Project model requires Department, so we'll skip if it couldn't be determined above.

                        # Ward Lookup (Mandatory for Project model)
                        ward = None
                        # Normalize names
                        sub_county_name_norm = sub_county_name_raw.replace("'", "").strip()
                        ward_name_norm = ward_name_raw.replace("'", "").strip()

                        # Handle 'Executive' case - skip as project requires specific ward
                        if sub_county_name_norm.lower() == 'executive' or ward_name_norm.lower() == 'executive':
                            self.stdout.write(self.style.WARNING(f"Skipping row {row_num} ('{project_name}'): Ward/SubCounty is 'Executive'. Model requires specific Ward."))
                            projects_skipped_count += 1
                            continue
                        # Handle missing Ward/SubCounty names
                        if not ward_name_norm or not sub_county_name_norm:
                            self.stdout.write(self.style.WARNING(f"Skipping row {row_num} ('{project_name}'): Ward ('{ward_name_raw}') or SubCounty ('{sub_county_name_raw}') name is missing."))
                            projects_skipped_count += 1
                            continue

                        # Perform lookup with specific name variations handled
                        ward_lookup_name = ward_name_raw
                        subcounty_lookup_name = sub_county_name_raw
                        if sub_county_name_raw == "Cherangany": subcounty_lookup_name = "Cherang'any"
                        if ward_name_raw == "Cherangany/Suwerwa": ward_lookup_name = "Cherang'any-Suwerwa"
                        if ward_name_raw.lower() == "chepsiro/kiptoror": ward_lookup_name = "Chepsiro-Kiptoror"

                        try:
                            ward = Ward.objects.get(
                                name__iexact=ward_lookup_name,
                                subcounty__name__iexact=subcounty_lookup_name
                            )
                        except Ward.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Skipping row {row_num} ('{project_name}'): Ward '{ward_lookup_name}' in SubCounty '{subcounty_lookup_name}' not found in DB."))
                            projects_skipped_count += 1
                            continue
                        except Ward.MultipleObjectsReturned:
                                self.stdout.write(self.style.ERROR(f"Error row {row_num} ('{project_name}'): Multiple Wards match '{ward_lookup_name}' / '{subcounty_lookup_name}'. Check data integrity."))
                                projects_skipped_count += 1
                                continue

                        # Percentage Complete
                        try:
                            percentage = int(float(raw_percentage)) if raw_percentage else 0
                            percentage = max(0, min(100, percentage)) # Clamp 0-100
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f"Row {row_num} ('{project_name}'): Invalid percentage '{raw_percentage}'. Setting to 0."))
                            percentage = 0

                        # Status
                        status = status_mapping.get(raw_status)
                        if not status:
                            # Infer status if not mapped
                            if percentage >= 100:
                                status = 'completed'
                            elif percentage > 0:
                                status = 'ongoing'
                            elif raw_status == 'under procurement': # Check for this specific status if present
                                status = 'under_procurement'
                            else:
                                status = 'not_started'
                            # Log inference only if status was provided but not mapped
                            if raw_status:
                                self.stdout.write(self.style.NOTICE(f"Row {row_num} ('{project_name}'): Status '{raw_status}' unmapped. Inferred as '{status}'."))

                        # Budget and Expenditure
                        try:
                            budget = Decimal(budget_raw) if budget_raw else Decimal('0.00')
                        except InvalidOperation:
                            self.stdout.write(self.style.WARNING(f"Row {row_num} ('{project_name}'): Invalid Budgeted Amount '{budget_raw}'. Setting to 0.00."))
                            budget = Decimal('0.00')

                        try:
                            # Using 'Project Cost' column for expenditure
                            expenditure = Decimal(expenditure_raw) if expenditure_raw else Decimal('0.00')
                        except InvalidOperation:
                            self.stdout.write(self.style.WARNING(f"Row {row_num} ('{project_name}'): Invalid Project Cost '{expenditure_raw}'. Setting to 0.00."))
                            expenditure = Decimal('0.00')

                        # Funding Source
                        funding_source = funding_source_mapping.get(funding_source_raw, 'county') # Default to county if unmapped

                        # --- Check for Existing Project BEFORE attempting creation ---
                        if Project.objects.filter(name=project_name, financial_year=financial_year).exists():
                            self.stdout.write(self.style.NOTICE(f"Skipping row {row_num} ('{project_name}'): Project already exists for FY {financial_year}."))
                            projects_skipped_existing += 1
                            projects_skipped_count += 1 # Also count as skipped overall
                            continue

                        # --- Create or Update Project ---
                        # Generate a unique slug incorporating the financial year start year
                        slug_base = slugify(project_name) if project_name else f"project-{row_num}"
                        slug = f"{slug_base}-{financial_year.split('-')[0]}"

                        defaults = {
                            'description': project_desc if project_desc else project_name,
                            'department': department, # Guaranteed to exist if capital, might be None if non-capital (model dependent)
                            'ward': ward, # Guaranteed to exist and be specific
                            'status': status,
                            'project_type': project_type,
                            'is_flagship': False, # Default, can be changed later
                            'start_date': start_date,
                            'end_date': end_date,
                            'percentage_complete': percentage,
                            'budget_allocation': budget,
                            'expenditure': expenditure,
                            'funding_source': funding_source,
                            'contractor_name': contractor,
                            'implementing_agency': implementing_agency_raw if implementing_agency_raw else None,
                            'google_map_location': google_map_url,
                            'challenges': remarks,
                            'slug': slug, # Include slug in defaults to allow updates
                        }

                        # Project does not exist, proceed with creation
                        try:
                            Project.objects.create(
                                name=project_name,
                                financial_year=financial_year,
                                **defaults
                            )
                            projects_created_count += 1
                        except Exception as create_error:
                            # Catch potential errors during creation (e.g., validation)
                            self.stdout.write(self.style.ERROR(f"Error creating project on row {row_num} ('{project_name}'): {create_error}"))
                            projects_skipped_count += 1
                            continue # Skip to next row on creation error

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file_path}")
        except CommandError as ce:
            raise ce # Re-raise CommandErrors
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nAn unexpected error occurred processing row {row_num} ('{project_name}'): {e}"))
            self.stdout.write(traceback.format_exc()) # Print full traceback for debugging
            self.stdout.write(self.style.ERROR("Transaction rolled back due to unexpected error."))
            # Optionally, re-raise the exception if you want the command to exit with non-zero status
            # raise CommandError(f"Seeding failed due to unexpected error. See traceback above.")

        # Final Report
        self.stdout.write(self.style.SUCCESS(f'\n--- CSV Seeding Complete ---'))
        self.stdout.write(f"Processed {processed_rows} rows from CSV.")
        self.stdout.write(self.style.SUCCESS(f'Successfully created {projects_created_count} new projects.'))
        self.stdout.write(self.style.NOTICE(f'Skipped {projects_skipped_existing} projects that already existed.'))
        if projects_skipped_count > 0:
             self.stdout.write(self.style.WARNING(f'Skipped {projects_skipped_count} rows due to missing/invalid data or lookup failures (check warnings above).'))
