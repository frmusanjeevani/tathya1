# TATHYA CASE MANAGEMENT SYSTEM - COMPLETE WORKFLOW ANALYSIS

## COMPREHENSIVE STAGE/MODULE FIELD ANALYSIS

---

## 1. CASE ENTRY/REGISTRATION MODULE

**Module Access:** Initiator, Investigator, Admin  
**Status Transition:** Draft → Submitted  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. BASIC CASE INFORMATION
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Case ID | Text Input (Auto-generated) | Yes | CASE20250728CE806A format | Unique case identifier |
| Category | Selectbox | Yes | Lending/Non-Lending | Case category classification |
| Referred By | Selectbox | Yes | 11 predefined options | Source of case referral |
| Type of Case | Selectbox | Yes | 20+ predefined options | Specific case type classification |
| LAN | Text Input | Yes | Alpha-numeric | Loan Account Number |
| Product | Selectbox | Yes | Database dropdown | Product classification |
| Region | Selectbox | Yes | Database dropdown | Geographic region |
| Case Date | Date Input | Yes | Max: Today | Case creation date |

#### B. CUSTOMER DEMOGRAPHICS & PROFILE
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Customer Name | Text Input | Yes | Text validation | Full customer name |
| Date of Birth | Date Input | Yes | Max: Today | Customer birth date |
| PAN | Text Input | Yes | 10 chars, alphanumeric | PAN card number |
| Mobile Number | Text Input | Yes | 10 digits | Contact number |
| Email ID | Text Input | Yes | Email format | Email address |
| Aadhaar Number | Text Input | No | 12 digits, auto-masked | Identity number (masked display) |
| Relationship Status | Selectbox | No | 5 predefined options | Marital status |
| Complete Address | Text Area | No | Multi-line text | Full address with pin code |

#### C. FINANCIAL PROFILE
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Occupation | Selectbox | No | 8 predefined options | Customer occupation |
| Monthly Income Range | Selectbox | No | 6 predefined brackets | Income classification |
| CIBIL Score | Number Input | No | 300-900 range | Credit score |

#### D. LOAN INFORMATION
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Branch/Location | Text Input | Yes | Text validation | Branch name |
| Loan Amount | Number Input | Yes | Min: 0, Currency format | Principal amount |
| Disbursement Date | Date Input | Yes | Max: Today | Loan disbursement date |

#### E. CASE DESCRIPTION
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Case Description | Text Area | Yes | Multi-line text | Detailed case description |

### DOCUMENT UPLOAD REQUIREMENTS:

#### IDENTITY DOCUMENTS (Choose upload method):
**Single Upload Method:**
- PAN Card Image (JPG, JPEG, PNG, PDF) - With preview
- Aadhaar Card Image (JPG, JPEG, PNG, PDF) - With preview  
- Customer Photo (JPG, JPEG, PNG) - With preview

**Bulk Upload Method:**
- Upload All Identity Documents at Once - Multiple file selection with preview

#### SUPPORTING DOCUMENTS:
- Bulk Supporting Documents Upload (PDF, DOC, DOCX, XLS, XLSX, JPG, JPEG, PNG)
- Multiple file selection with preview and file details

#### VERIFICATION FEATURES:
- Identity Verification Tab (appears when PAN + Customer Photo uploaded)
- AI-powered comparison between PAN card photo and customer photo
- Document preview and validation

---

## 2. CASE ALLOCATION MODULE

**Module Access:** Investigator, Admin  
**Status Transition:** Submitted → Allocated/Under Investigation  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. CASE SELECTION & ASSIGNMENT
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Case Selection | Dropdown | Yes | Database cases | Select from submitted cases |
| Investigation Type | Radio Button | Yes | Agency/Regional | Investigation method choice |
| Assigned Investigator | Selectbox | Yes | Database users | Investigator assignment |
| Priority Level | Selectbox | Yes | High/Medium/Low | Case priority |
| Expected Completion | Date Input | Yes | Future date | Target completion date |

#### B. ALLOCATION NOTES
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Allocation Notes | Text Area | Yes | Multi-line text | Assignment instructions |
| Special Instructions | Text Area | No | Multi-line text | Additional guidance |

### ACTIONS AVAILABLE:
- Allocate to Agency Investigation
- Allocate to Regional Investigation  
- Return to Case Entry (with comments)
- Generate SMS notification to assigned investigator

---

## 3. INVESTIGATION MODULE (Agency/Regional)

**Module Access:** Investigator, Admin  
**Status Transition:** Allocated → Under Investigation → Primary Review  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. INVESTIGATION DETAILS FORM
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Investigation Method | Selectbox | Yes | 8 predefined options | Investigation approach |
| Field Visit Conducted | Radio Button | Yes | Yes/No | Physical verification |
| Customer Contacted | Radio Button | Yes | Yes/No | Direct contact status |
| Documents Verified | Radio Button | Yes | Yes/No | Document verification |
| Inconsistencies Found | Radio Button | Yes | Yes/No | Discrepancy identification |

#### B. DETAILED FINDINGS
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Investigation Findings | Text Area | Yes | Multi-line text | Detailed findings |
| Risk Assessment | Selectbox | Yes | Low/Medium/High/Critical | Risk evaluation |
| Fraud Indicators | Text Area | No | Multi-line text | Suspicious indicators |
| Recommended Action | Selectbox | Yes | 8 predefined options | Next steps recommendation |

#### C. VERIFICATION STATUS
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Identity Verification | Selectbox | Yes | Verified/Partial/Failed | ID verification status |
| Address Verification | Selectbox | Yes | Verified/Partial/Failed | Address verification status |
| Income Verification | Selectbox | Yes | Verified/Partial/Failed | Income verification status |
| Employment Verification | Selectbox | Yes | Verified/Partial/Failed | Employment verification status |

#### D. INVESTIGATION SUMMARY
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Investigation Summary | Text Area | Yes | Multi-line text | Summary of investigation |
| Recommendation | Text Area | Yes | Multi-line text | Final recommendation |

### ACTIONS AVAILABLE:
- Submit to Primary Review
- Request Additional Information
- Close Investigation (with reason)
- Generate Investigation Report (PDF)

---

## 4. PRIMARY REVIEW MODULE

**Module Access:** Reviewer, Investigator, Admin  
**Status Transition:** Under Investigation → Approved/Rejected/Final Review  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. REVIEW ASSESSMENT
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Review Status | Radio Button | Yes | Approve/Reject/Info Request | Review decision |
| Review Comments | Text Area | Yes | Multi-line text | Review feedback |
| Quality Score | Number Input | No | 1-10 scale | Investigation quality rating |

#### B. ADDITIONAL REVIEW FIELDS
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Compliance Check | Checkbox | No | Boolean | Compliance verification |
| Policy Adherence | Checkbox | No | Boolean | Policy compliance check |
| Documentation Complete | Checkbox | No | Boolean | Documentation completeness |

### INTERACTION CHANNELS:
- Request Missing Information system
- Comment tracking and response handling
- Data flow from multiple investigation sources

### ACTIONS AVAILABLE:
- Approve to Final Review
- Reject to Investigation
- Request Additional Information
- Generate Review Report

---

## 5. FINAL REVIEW MODULE

**Module Access:** Reviewer, Admin  
**Status Transition:** Approved → Legal Review (parallel processing)  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. FINAL REVIEW SUMMARY
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Final Review Summary | Text Area | Yes | Multi-line text | Comprehensive case summary |
| AI Generated Summary | Text Area (Read-only) | No | AI-generated | AI-powered case analysis |
| Legal Action Required | Radio Button | Yes | Yes/No | Legal processing requirement |
| Actioner Required | Radio Button | Yes | Yes/No | Closure action requirement |

#### B. AI ENHANCEMENT FEATURES
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| AI Assist Button | Button | No | N/A | Generate AI summary |
| Accept AI | Button | No | N/A | Accept AI suggestion |
| Regenerate AI | Button | No | N/A | Generate new AI summary |
| Dismiss AI | Button | No | N/A | Reject AI suggestion |

### ACTIONS AVAILABLE:
- Send to Legal Review
- Send to Actioner (Closure)
- Send to Both (Parallel processing)
- Return to Primary Review

---

## 6. APPROVER 1 MODULE

**Module Access:** Approver, Admin  
**Status Transition:** Approved → Second Approval  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. APPROVAL DECISION
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Approval Status | Radio Button | Yes | Approve/Reject/Return | Approval decision |
| Approval Comments | Text Area | Yes | Multi-line text | Approval feedback |
| Conditions/Remarks | Text Area | No | Multi-line text | Additional conditions |

### ACTIONS AVAILABLE:
- Approve to Approver 2
- Reject to Primary Review
- Request Additional Information
- Return to Previous Stage

---

## 7. APPROVER 2 MODULE

**Module Access:** Approver, Admin  
**Status Transition:** Second Approval → Final Review  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. FINAL APPROVAL
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Final Approval Status | Radio Button | Yes | Approve/Reject/Return | Final approval decision |
| Final Approval Comments | Text Area | Yes | Multi-line text | Final approval feedback |
| Executive Summary | Text Area | No | Multi-line text | Executive level summary |

### ACTIONS AVAILABLE:
- Approve to Final Review
- Reject to Approver 1
- Return to Primary Review
- Escalate to Higher Authority

---

## 8. LEGAL PANEL MODULE

**Module Access:** Legal Reviewer, Admin  
**Status Transition:** Legal Review → Legal Action/Closed  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. LEGAL REVIEW
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Legal Review Status | Selectbox | Yes | Multiple options | Legal decision |
| Legal Comments | Text Area | Yes | Multi-line text | Legal analysis |
| Legal Action Type | Selectbox | Yes | SCN/Order/Opinion/Notice | Type of legal action |

#### B. DOCUMENT GENERATION
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Show Cause Notice | Text Area | Conditional | Multi-line text | SCN content |
| Reasoned Order | Text Area | Conditional | Multi-line text | Order content |
| Legal Opinion | Text Area | Conditional | Multi-line text | Opinion content |
| Recovery Notice | Text Area | Conditional | Multi-line text | Notice content |

### DOCUMENT GENERATION:
- Show Cause Notice (SCN) with customizable content
- Reasoned Order with legal formatting
- Legal Opinion documentation
- Recovery Notice generation
- PDF download functionality for all documents

### ACTIONS AVAILABLE:
- Issue Show Cause Notice
- Generate Reasoned Order
- Provide Legal Opinion
- Send Recovery Notice
- Close Legal Review
- Return to Final Review

---

## 9. CLOSURE/ACTIONER MODULE

**Module Access:** Actioner, Admin  
**Status Transition:** Legal Review → Closed  
**Page Template:** Case Allocation format with professional styling  

### SECTIONS & FIELDS:

#### A. CLOSURE DECISION
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Closure Type | Radio Button | Yes | Fraud/Non-Fraud | Case classification |
| Closure Action | Selectbox | Yes | Multiple options | Closure method |
| Recovery Amount | Number Input | Conditional | Currency format | Amount recovered |
| Closure Reason | Text Area | Yes | Multi-line text | Closure justification |

#### B. FRAUD CLASSIFICATION (if Fraud selected)
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Fraud Type | Selectbox | Yes | Multiple options | Type of fraud |
| Fraud Amount | Number Input | Yes | Currency format | Fraud value |
| Fraud Status | Selectbox | Yes | Confirmed/Suspected | Fraud confirmation |

#### C. CLOSURE DETAILS
| Field Name | Field Type | Required | Validation | Description |
|------------|------------|----------|------------|-------------|
| Final Action | Selectbox | Yes | 8+ predefined options | Final closure action |
| Settlement Details | Text Area | Conditional | Multi-line text | Settlement information |
| Write-off Details | Text Area | Conditional | Multi-line text | Write-off justification |
| Transfer Details | Text Area | Conditional | Multi-line text | Transfer information |

### ACTIONS AVAILABLE:
- Close as Fraud (with sub-classification)
- Close as Non-Fraud
- Recovery Closure
- Settlement
- Write-off
- Transfer to Legal
- Return to Final Review

---

## DATABASE SCHEMA OVERVIEW

### MAIN TABLES:
1. **cases** - Primary case table with 45+ fields
2. **users** - User management with role-based access
3. **case_comments** - Comment tracking system
4. **case_documents** - Document management
5. **investigation_details** - Investigation specific data
6. **audit_logs** - Complete audit trail
7. **workflow_data** - Stage-specific workflow data

### KEY DATABASE FIELDS (cases table):
- Status tracking fields (reviewed_by, approved_by, legal_reviewed_by, closed_by)
- Timestamp fields (created_at, updated_at, reviewed_at, approved_at, etc.)
- SLA tracking (fmr1_due_date, fmr3_due_date, document_retention_date)
- Customer demographics (25+ fields)
- Case classification (risk_category, case_source, kyc_status)

---

## WORKFLOW PROGRESSION SUMMARY

**Complete Flow:** Case Entry → Case Allocation → Investigation (Agency/Regional) → Primary Review → Final Review → Approver 1 → Approver 2 → Final Review → Legal & Actioner (Parallel) → Closed

**Status Transitions:**
1. Draft → Submitted (Case Entry)
2. Submitted → Allocated (Case Allocation)
3. Allocated → Under Investigation (Investigation)
4. Under Investigation → Primary Review (Investigation Complete)
5. Primary Review → Approved (Review Complete)
6. Approved → Second Approval (Approver 1)
7. Second Approval → Final Review (Approver 2)
8. Final Review → Legal Review (Parallel processing)
9. Legal Review → Closed (Final closure)

**Document Support:** All modules support comprehensive document upload, preview, and management with audit trails and secure file handling across 8+ file formats.

**AI Integration:** Gemini AI integration across multiple modules for smart suggestions, auto-completion, document analysis, and professional summary generation.

**Interaction Channels:** Cross-stage communication system for requesting missing information with standardized tracking and response handling.

---

*Analysis completed: January 2025*
*Total Fields Analyzed: 150+ across 9 major workflow stages*
*Document Types Supported: 8+ formats with comprehensive upload and preview*
*Database Schema: 7 main tables with 45+ case-specific fields*