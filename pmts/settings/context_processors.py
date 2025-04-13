from .models import HeaderSettings, FooterSettings, PageSettings
from django.templatetags.static import static
from django.conf import settings

def header_settings(request):
    try:
        header = HeaderSettings.objects.first()
        if not header:
            header = HeaderSettings(
                logo='',
                twitter_url='#',
                facebook_url='#',
                instagram_url='#',
                login_url='#'
            )
        header.logo_static = header.logo.url if header.logo else static('img/logo.png')
    except HeaderSettings.DoesNotExist:
        header = HeaderSettings(
            logo='',
            twitter_url='#',
            facebook_url='#',
            instagram_url='#',
            login_url='#'
        )
        header.logo_static = static('img/logo.png')

    try:
        footer = FooterSettings.objects.first()
        if not footer:
            footer = FooterSettings(
                cgtn_pmts_text="CGTN PMTS",
                about_text="The PMTS provides comprehensive information on all county projects, ensuring transparency and accountability in project management across Trans-Nzoia County.",
                financial_years=[
                    {'text': 'FY 2022-2023', 'url': '/fy-2022-2023/'},
                    {'text': 'FY 2023-2024', 'url': '/fy-2023-2024/'},
                    {'text': 'FY 2024-2025', 'url': '/fy-2024-2025/'},
                ],
                quick_links=[
                    {'text': 'Public Dashboard', 'url': '/dashboard/'},
                    {'text': 'Projects Gallery', 'url': '/gallery/'},
                    {'text': 'FAQs', 'url': '/faqs/'},
                ],
                contact_phone="254720031035",
                contact_email="info@transnzoia.go.ke",
                contact_address="P.O BOX 1683\nKitale, Trans-Nzoia County",
                twitter_url='#',
                facebook_url='#',
                instagram_url='#',
                copyright_year="2025",
                copyright_text="COUNTY GOVERNMENT OF TRANS-NZOIA\nALL RIGHTS RESERVED."
            )
    except FooterSettings.DoesNotExist:
        footer = FooterSettings(
            cgtn_pmts_text="CGTN PMTS",
            about_text="The PMTS provides comprehensive information on all county projects, ensuring transparency and accountability in project management across Trans-Nzoia County.",
            financial_years=[
                {'text': 'FY 2022-2023', 'url': '/fy-2022-2023/'},
                {'text': 'FY 2023-2024', 'url': '/fy-2023-2024/'},
                {'text': 'FY 2024-2025', 'url': '/fy-2024-2025/'},
            ],
            quick_links=[
                {'text': 'Public Dashboard', 'url': '/dashboard/'},
                {'text': 'Projects Gallery', 'url': '/gallery/'},
                {'text': 'FAQs', 'url': '/faqs/'},
            ],
            contact_phone="254720031035",
            contact_email="pmts@transnzoia.go.ke",
            contact_address="P.O BOX 1683\nKitale, Trans-Nzoia County",
            twitter_url='#',
            facebook_url='#',
            instagram_url='#',
            copyright_year="2025",
            copyright_text="COUNTY GOVERNMENT OF TRANS-NZOIA\nALL RIGHTS RESERVED."
        )

    try:
        page_settings = PageSettings.objects.first()
        if not page_settings:
            page_settings = PageSettings(
                about_content="Welcome to PMTS, a platform dedicated to transparent project management in Trans-Nzoia County.\nLearn more at our website.",
                intro_title="What is PMTS?",
                intro_description="The Projects Monitoring and Tracking System (PMTS) is a platform developed by the County Government of Trans-Nzoia to oversee and manage development projects.\nIt ensures transparency and accountability.",
                mission="To deliver a transparent and efficient system for monitoring county projects.\nWe aim to empower stakeholders with real-time data.",
                vision="To lead in project management innovation, fostering trust and participation across Trans-Nzoia County.",
                core_values="Integrity: Upholding ethical standards.\nInnovation: Embracing new solutions.\nInclusivity: Engaging all stakeholders.",
                objectives=[
                    {
                        "title": "Transparency",
                        "description": "Ensure all project details are accessible to the public in real-time.",
                        "icon": "bi-eye-fill"
                    },
                    {
                        "title": "Accountability",
                        "description": "Track responsibilities and performance for all county projects.",
                        "icon": "bi-shield-check"
                    },
                    {
                        "title": "Efficiency",
                        "description": "Streamline project management processes to save time and resources.",
                        "icon": "bi-gear-fill"
                    },
                ],
                faqs=[
                    {
                        "question": "What is the Projects Monitoring and Tracking System (PMTS)?",
                        "answer": "PMTS is a digital platform designed by the County Government of Trans-Nzoia to improve the management, monitoring, and evaluation of county projects.\nIt provides real-time data to stakeholders."
                    },
                    {
                        "question": "How does PMTS enhance transparency and accountability?",
                        "answer": "PMTS promotes transparency by making project data publicly accessible in real-time.\nIt ensures accountability through detailed tracking of project progress and responsibilities."
                    },
                ],
                contact_address="P.O BOX 1683\nKitale, Trans-Nzoia County",
                contact_email="info@transnzoia.go.ke",
                contact_phone="+254720031035",
                contact_office_hours="Monday - Friday: 8:00 AM - 5:00 PM",
                contact_departments=[
                    {"name": "County Secretary", "emails": ["countysecretary@transnzoia.go.ke"]},
                    {
                        "name": "Department of Trade, Industrialization, Tourism & Cooperative Development",
                        "emails": ["trade@transnzoia.go.ke", "tourism@transnzoia.go.ke"]
                    },
                    {"name": "Department of Finance & Economic Planning", "emails": ["finance@transnzoia.go.ke"]},
                ]
            )
    except PageSettings.DoesNotExist:
        page_settings = PageSettings(
            about_content="Welcome to PMTS, a platform for Trans-Nzoia County.",
            intro_title="What is PMTS?",
            intro_description="The Projects Monitoring and Tracking System (PMTS) is a platform developed by the County Government of Trans-Nzoia.",
            mission="To deliver a transparent and efficient system.",
            vision="To lead in project management innovation.",
            core_values="Integrity, Innovation, Inclusivity.",
            objectives=[
                {
                    "title": "Transparency",
                    "description": "Ensure all project details are accessible.",
                    "icon": "bi-eye-fill"
                },
            ],
            faqs=[
                {
                    "question": "What is PMTS?",
                    "answer": "A digital platform for project management."
                },
            ],
            contact_address="P.O BOX 1683\nKitale",
            contact_email="info@transnzoia.go.ke",
            contact_phone="+254720031035",
            contact_office_hours="Monday - Friday: 8:00 AM - 5:00 PM",
            contact_departments=[
                {"name": "County Secretary", "emails": ["countysecretary@transnzoia.go.ke"]},
                {
                    "name": "Department of Trade, Industrialization, Tourism & Cooperative Development",
                    "emails": ["trade@transnzoia.go.ke", "tourism@transnzoia.go.ke"]
                },
            ]
        )

    return {
        'header_settings': header,
        'footer_settings': footer,
        'page_settings': page_settings
    }