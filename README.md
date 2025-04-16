# Trans-Nzoia County Projects Monitoring & Tracking System (PMTS)

A comprehensive web-based application for managing, tracking, and reporting on county development projects.

![Trans-Nzoia County PMTS](https://via.placeholder.com/1200x400?text=Trans-Nzoia+County+PMTS)

## Overview

The Trans-Nzoia County Projects Monitoring & Tracking System (PMTS) is designed to enhance transparency and accountability in the management of county development projects. It provides a centralized platform for tracking project progress, budget utilization, and performance across different departments and locations within the county.

## Key Features

- **Project Management**: Create, update, and track projects with comprehensive details
- **Multi-level Dashboards**: Tailored views for executives, departments, and public users
- **Financial Tracking**: Monitor budget allocation and expenditure for each project
- **Location-based Visualization**: View projects by sub-county and ward with interactive maps
- **Progress Monitoring**: Track project milestones and completion percentages
- **Public Feedback**: Allow citizens to provide feedback on projects
- **Department-specific Views**: Filter projects by department
- **User Role Management**: Different access levels for executives, departmental staff, and public users
- **Project Photos**: Upload and display visual documentation of project progress
- **Reporting**: Generate detailed reports on project status and budget utilization

## Technology Stack

- **Backend**: Django (Python web framework)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Charts & Visualization**: Chart.js
- **Maps**: Integration with Google Maps for project locations

## Installation and Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip (Python package manager)
- virtualenv (recommended)

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd county_pmts
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**

   Create a PostgreSQL database and configure it in `county_pmts/settings.py` or create a `.env` file with the following variables:

   ```
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=your_secret_key
   ```

5. **Run migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Seed initial data**

   ```bash
   # Seed departments
   python manage.py loaddata departments_data.json

   # Seed locations (county, sub-counties, wards)
   python manage.py loaddata locations_data.json

   # (Optional) Seed demo projects
   python manage.py seed_projects --projects 250
   ```

8. **Run the development server**

   ```bash
   python manage.py runserver
   ```

9. **Access the application**

   The application will be available at http://127.0.0.1:8000/

## System Structure

### User Roles

- **Executive Level**: Governor, Deputy Governor, County Secretary
  - Access to all departments and projects
  - High-level dashboards and reports

- **Departmental Level**: CEC Members, Chief Officers, Directors
  - Access to projects within their department
  - Department-specific dashboards and reports

- **Public Level**: Citizens, Media, NGOs
  - Read-only access to public projects
  - Ability to submit feedback on projects

### Key Applications

1. **Accounts**: User authentication and profile management
2. **Projects**: Core project management functionality
3. **Departments**: Department structure and management
4. **Locations**: County, Sub-county, and Ward management
5. **Dashboard**: Analytics and visualization

## Project Data Specifications

Each project in the system includes:

### Basic Information
- Project Name
- Description
- Department
- Sub-County & Ward
- Status (Completed, Ongoing, Stalled, Not Started, Under Procurement)
- Start Date & Expected End Date
- Percentage Completion

### Financial Information
- Budget Allocation
- Expenditure
- Funding Source (County, National Government, Donors)

### Implementation Details
- Contractor Name
- Implementing Agency
- Project Photos
- Google Map Location

### Monitoring & Feedback
- Challenges Encountered
- Public Feedback

## Dashboard & Insights

### Executive Dashboard
- Total Projects (Completed/Ongoing/Stalled)
- Budget Absorption Rate
- Departmental Expenditure vs. Allocation
- Projects by Sub-County/Ward
- Alerts for delayed projects and budget overruns

### Departmental Dashboard
- Department-specific projects
- Budget vs. Expenditure trends
- Project status breakdown
- Recent projects

### Public Dashboard
- Project explorer with search and filter capabilities
- Project details and timelines
- Feedback submission system

## Usage Guidelines

### Adding a New Project

1. Log in with appropriate credentials
2. Navigate to Projects > Add New Project
3. Fill in all required details
4. Upload any initial project photos
5. Save the project

### Updating Project Progress

1. Navigate to the specific project
2. Click on "Add Progress Update"
3. Enter the current completion percentage and description
4. Submit the update

### Generating Reports

1. Navigate to the Reports section
2. Select report type and parameters
3. Generate the report in desired format (PDF/Excel)

## Development

### Project Structure

```
county_pmts/
├── accounts/            # User authentication and profiles
├── dashboard/           # Dashboard views and logic
├── departments/         # Department models and views
├── locations/           # Location (county, sub-county, ward) models
├── projects/            # Core project management functionality
├── county_pmts/         # Main settings and configuration
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
├── media/               # User-uploaded files (project photos)
└── requirements.txt     # Project dependencies
```

### Running Tests

```bash
python manage.py test
```

## License

[Insert License Information Here]

## Contact

For support or inquiries, please contact:

- Project Manager: [Name](mailto:email@example.com)
- Technical Support: [Name](mailto:tech@example.com)

---

© 2024 Trans-Nzoia County Government. All rights reserved.