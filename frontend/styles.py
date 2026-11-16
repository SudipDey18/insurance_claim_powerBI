"""
Styles Module
Provides a minimalist, professional CSS design system.
Strictly free of emojis, stickers, and decorative clutter.
Proper element scaling and compact executive proportions.
"""

def get_minimal_css() -> str:
    """Returns CSS styles for a minimal, executive corporate interface."""
    return """
    <style>
        /* Base typography and container constraints */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #0F172A;
        }

        /* Control main page max-width and top padding for proper visual scaling */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
        }

        /* Hide Streamlit top header clutter while keeping clean look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Top Navbar Container */
        .navbar-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 16px;
            background-color: #FFFFFF;
            border-bottom: 1px solid #E2E8F0;
            margin-bottom: 12px;
        }
        .navbar-brand {
            font-size: 1.05rem;
            font-weight: 700;
            color: #1E3A8A;
            letter-spacing: -0.3px;
        }
        .navbar-subtitle {
            font-size: 0.75rem;
            color: #64748B;
            font-weight: 400;
        }

        /* Minimal KPI Metric Cards */
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }
        .metric-label {
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748B;
            margin-bottom: 2px;
        }
        .metric-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
        }
        .metric-caption {
            font-size: 0.7rem;
            color: #94A3B8;
            margin-top: 2px;
        }

        /* Section Headings */
        .view-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 2px;
            letter-spacing: -0.3px;
        }
        .view-description {
            font-size: 0.82rem;
            color: #475569;
            margin-bottom: 12px;
        }
        .section-title {
            font-size: 0.92rem;
            font-weight: 600;
            color: #1E293B;
            margin-top: 14px;
            margin-bottom: 8px;
            border-bottom: 1px solid #F1F5F9;
            padding-bottom: 4px;
        }

        /* Status Banners */
        .banner-pass {
            background-color: #F8FAFC;
            border-left: 3px solid #16A34A;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.8rem;
            color: #15803D;
            margin-bottom: 8px;
        }
        .banner-alert {
            background-color: #FEF2F2;
            border-left: 3px solid #DC2626;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.8rem;
            color: #991B1B;
            margin-bottom: 8px;
        }

        /* Clean badges */
        .status-badge {
            display: inline-block;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-online {
            background-color: #F0FDF4;
            color: #166534;
            border: 1px solid #BBF7D0;
        }
        .badge-offline {
            background-color: #FFFBEB;
            color: #92400E;
            border: 1px solid #FDE68A;
        }
        .badge-viewers {
            background-color: #EFF6FF;
            color: #1E40AF;
            border: 1px solid #BFDBFE;
        }
        .badge-dataset {
            background-color: #F1F5F9;
            color: #334155;
            border: 1px solid #CBD5E1;
        }

        /* Radio buttons horizontal styling for Navbar */
        div[data-testid="stHorizontalBlock"] {
            align-items: center;
        }

        /* Subtle borders on visual chart wrappers */
        .stPlotlyChart, .stImage, div[data-testid="stArrowVegaLiteChart"] {
            margin-bottom: 8px;
        }
    </style>
    """
