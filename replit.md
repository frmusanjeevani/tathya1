# Tathya - Case Management System

## Overview

Tathya is a comprehensive case management system built with Streamlit for managing legal/compliance cases within an organization. It provides role-based access control for Initiators, Reviewers, Approvers, Legal Reviewers, Action Closure Authorities (Actioners), and Administrators. The system manages the complete lifecycle of cases from creation to closure, including audit trails and document management. Tathya aims to streamline case workflows, enhance compliance, and provide robust analytics for organizational legal and risk management.

## User Preferences

Preferred communication style: Simple, everyday language.
Case display format: Simple plain text lists without any HTML formatting, styling, or tables.
AI assistant features: Permanently banned and must never be re-added.
Naming consistency: "Tathya Verification Lab" renamed to "Configuration Panel" system-wide (January 2025).
Navigation structure: Configuration Panel removed from login page selection, now only accessible through Investigation system's left navigation panel for Admin and Investigator roles.
New system: Created dedicated "Tathya Lab" page with verification basket organized by categories, accessible from login page alongside Investigation system (January 2025).
Internal Fraud Management Workflow: Complete role-based workflow system with 8 distinct sections accessible through left panel navigation, including separate Approver 1 and Approver 2 sections, dark blue theme implementation, and independent section-wise data saving (January 2025).
No-code workflow builder: Advanced drag-and-drop interface for creating custom verification workflows with API integration, visual node connections, and template system (January 2025).
Data flow architecture: Comprehensive system ensuring seamless data flow between all workflow stages with interaction channels for communication and standardized page formatting across all modules (January 2025).
3D intro animation: Extended 8-9 second Three.js animation with dynamic text cycling (Investigation, Verification, Analytics, etc.), pause/resume control in bottom-right corner, rotating 3D logo, and particle effects. Auto-redirects to login with CSS fallback for reliability (January 2025).

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **UI/UX Decisions**:
    - Modern glassmorphism design with professional gradients, animations, and hover effects.
    - Consistent branding with logos and corporate color themes.
    - Professional iconography and typography (Aptos font family).
    - Customizable user dashboards with various widget types and layout options.
    - Expandable navigation panels and standardized, professional case display formats (card-based, grid layouts).
    - **Investigation Intelligence Branding**: Unified "🕵️‍♂️ Tathya Investigation Intelligence" header across all Investigation workflow pages with AI-styled gradient design and standardized sub-headers with professional typography.
    - **Standardized Page Format**: All workflow stages now use consistent Case Allocation page template with standardized headers, subheaders, and professional box styling (#f5f5f5 backgrounds with 80% black text).
    - **3D Intro Animation**: Modern animated intro page featuring Three.js 3D graphics with rotating torus geometry, orbiting spheres, particle starfield background, and professional gradient branding. Auto-redirects to login after 8-9 second animation with CSS fallback for reliability.
- **UI Pattern**: Multi-page application with role-based navigation.
- **Layout**: Wide layout with responsive columns and tabs.
- **State Management**: Streamlit session state for authentication and user context.
- **Navigation**: Sidebar-based navigation with role-specific menu options, organized into logical sections (Case Management, Analytics, Admin, Utility). Admin section contains System Administration and Role Management, while Utility contains AI tools and verification modules. Main Investigation button rebranded to "🕵️‍♂️ Tathya Investigation Intelligence" with standardized professional sub-headers and hover effects.

### Backend Architecture
- **Application Layer**: Python-based business logic with modular page structure.
- **Authentication**: Professional login page with secure authentication system, user ID/password login, session management, and flexible role-based access control (including "All Roles Access" for specific users). Features login attempt tracking and account lockout protection.
- **Authorization**: Role-based access control with decorators.
- **Database Layer**: SQLite database with context manager pattern, including login audit logging.
- **File Management**: Local file system for document uploads with organized directory structure.

### Technical Implementations & Feature Specifications
- **Case Entry**: Comprehensive forms for case registration, including demographic details, identity document image management (PAN, Aadhaar, Customer Photo), and other supporting documents (Business, Property, Additional). Features include auto-generated Case IDs, masked Aadhaar display, dedicated Identity Verification tab, and seamless data flow integration to Case Allocation module upon submission (January 2025).
- **User Management**: Comprehensive user master system with detailed profiles, team assignments, and referral mappings. Admin users can view, add, edit, and soft-delete users, and manage "All Roles Access".
- **Case Management Workflow**:
    - **Workflow Sequence**: Initiator → Primary Review → Investigation → Final Adjudication → Categorized Routing (Fraud → Legal Compliance Center → Regulatory Reporting; Non-Fraud → Case Closure; Other Incident → Stakeholder Actioner).
    - **Investigation Panel**: Features case auto-fetch, detailed investigation forms (document/field verification), case assignment options (Closure, Regional, Agency), and PDF report generation. Includes risk score analysis and seamless Case Allocation module with auto-populated forms from New Case Registration submissions (January 2025).
    - **Regional Investigation**: Complete regional investigation workflow replicating agency structure with standardized formatting and data flow integration.
    - **Reviewer/Approver Panels**: Standardized case details display, clear status transitions, and integration with the overall workflow. Enhanced Primary Review receives inputs from Case Allocation, Agency Investigation, and Regional Investigation.
    - **Final Adjudication Panel**: Replaces Final Review Authority with comprehensive categorization logic (Fraud/Non-Fraud/Other Incident), AI-powered adjudication summaries, and intelligent workflow routing based on case categorization (January 2025).
    - **Legal Compliance Center**: Enhanced Legal Panel supporting fraud processing, various legal action types (SCN, Reasoned Order, Legal Opinion, Recovery Notice) with sequential workflow, and integration with Regulatory Reporting module.
    - **Regulatory Reporting Module**: New FMR1 compliance and RBI reporting center for fraud cases, featuring automated report generation, submission tracking, and regulatory analytics (January 2025).
    - **Stakeholder Actioner Module**: New task and action orchestration center for managing internal and external stakeholder communications, task assignments, progress tracking, and comprehensive action reporting (January 2025).
    - **Case Closure Panel**: Comprehensive action recommendations, risk level evaluation, and sequential action types (Recovery Closure, Settlement, Write-off, Transfer to Legal).
    - **Internal Fraud Management Workflow**: Complete standalone workflow system with 8 role-specific sections (Case Initiation, Case Allocation, Investigation, Review & Assessment, Approver 1 Decision, Approver 2 Decision, Code of Conduct, Closure Process) accessible through left panel navigation. Features dark blue theme (#0D3B66 primary, #09427A hover), independent section-wise data saving, comprehensive database integration, and role-based access control ensuring each workflow section is accessible only by respective roles (January 2025).
    - **Document Management**: Supports multiple document formats (PDF, JPG, PNG, DOCX, XLS, XLSX) with secure file handling and audit logging.
    - **Interaction Channels System**: Communication system between workflow stages for requesting missing information with standardized comment/request tracking and response handling.
    - **Comprehensive Data Flow Manager**: Seamless data flow from Case Registration → Case Allocation → Investigation stages → Primary Review → Final Adjudication → Categorized Routing with stage data preservation and intelligent workflow progress tracking.

- **Smart Verification & Risk Detection Suite**: AI-driven platform with modules for Face Match Intelligence (dual-service: DeepFace AI with 6 models locally + Face++ Cloud API), Signature Verification, Document Consistency, OCR & Field Extraction, Bank Statement Analyzer, Anomaly Detection, ID Validation, Inter-Document Cross-Check, Suspicious Pattern Triggering, and Digital Identity DNA Mapping. All modules use Google Gemini AI for enhanced analysis. Includes a "One-Click Document Verification" workflow with bulk upload and automated categorization.
- **Enhanced Risk Assessment**: Comprehensive Risk Score & Speedometer with 25+ parameters across 5 categories (Personal, Financial, Property, Business, Advanced Risk Factors), featuring tabbed interface and multi-dimensional AI analysis.
- **MNRL Verification Enhancement**: Mobile Number Revocation List verification now extracts customer details (name, customer ID, registration date, plan details, KYC status) from API responses when available.
- **AI Integration**: Gemini-powered AI Assistant for smart case analysis, document generation, interactive chat, and auto-suggestions/completion in remarks fields. Includes "Enhance Description" feature in case entry forms.
- **Dashboard**: Customizable user dashboards with role-based widgets (Case Statistics, My Cases Summary, Status Distribution, Recent Activity, Priority Cases, Timeline View, Performance Metrics, Workflow Progress). Includes TAT metrics and interactive Plotly charts.
- **Audit System**: Comprehensive audit logging for all case modifications and user actions, including timestamps and user attribution.
- **Error Handling**: Comprehensive system with formatted error boxes, contextual emojis, and integrated logging for various error types (Database, File, Validation, Permission, API).

## External Dependencies

- **Core Libraries**:
    - **Streamlit**: Web application framework.
    - **SQLite3**: Database connectivity.
    - **Pandas**: Data manipulation.
    - **Plotly**: Interactive visualization charts.
    - **Hashlib**: Password security (SHA-256).
    - **ReportLab**: PDF report generation.
- **Third-Party Services/APIs**:
    - **Google Gemini API**: Primary provider for AI-powered case analysis, document generation, smart suggestions, and all verification/analysis tasks across the platform.
    - **DeepFace Library**: Fallback provider for facial recognition using multiple deep learning models (VGG-Face, Facenet, OpenFace, DeepFace, DeepID, ArcFace, Dlib, SFace).
    - **Google Vision API**: Additional fallback option for face verification.
    - **Twilio**: For SMS notifications (e.g., investigation assignment alerts).
- **Deep Learning Dependencies**:
    - **TensorFlow**: Backend for DeepFace neural network models.
    - **OpenCV-Python**: Computer vision library for image processing and face detection.
    - **DeepFace**: Advanced facial recognition library with multiple model support.
- **File System Dependencies**:
    - `uploads/`: Directory for case documents.
    - `exports/`: Directory for exported reports.
    - `case_management.db`: SQLite database file.