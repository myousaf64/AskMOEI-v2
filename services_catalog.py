"""
services_catalog.py
Structured catalog of all 10 MOEI maritime services derived from the knowledge base.
Portal paths verified against the step-by-step guides in knowledge_base/.
"""

SERVICES: dict[str, dict] = {
    "pleasure_boat_renewal": {
        "name": "Renewal of Pleasure Boat Registration",
        "name_ar": "تجديد تسجيل قارب النزهة أو ترخيصه",
        "category": "Pleasure Boat Services",
        "keywords": [
            "renew", "renewal", "pleasure boat", "boat registration",
            "boat license", "قارب", "تجديد", "تسجيل",
        ],
        "url": "https://www.moei.gov.ae/en/services/renewal-of-pleasure-boat-registration",
        "portal_path": "Services Directory → Maritime Transportation → Renewal of pleasure boat registration",
        "requires_uae_pass": True,
        "required_info": ["Official Number", "Boat Name in English"],
        "delivery": "Certificate issued automatically by email after approval; also downloadable from dashboard.",
        "intents": ["vessel_renewal", "boat_renewal"],
        "related": ["pleasure_boat_deletion", "mortgage_deletion"],
    },
    "pleasure_boat_deletion": {
        "name": "Issuing Deletion Pleasure Boat Certificate",
        "name_ar": "إصدار شهادة شطب قارب النزهة",
        "category": "Pleasure Boat Services",
        "keywords": [
            "delete", "deletion", "cancel", "cancellation",
            "pleasure boat", "certificate", "شطب", "قارب", "إلغاء",
        ],
        "url": "https://www.moei.gov.ae/en/services/issuing-deletion-pleasure-boat-certificate",
        "portal_path": "Services Directory → Maritime Transportation → Issuing deletion pleasure boat certificate",
        "requires_uae_pass": True,
        "required_info": ["Official Number", "Boat Name in English"],
        "delivery": "Certificate issued automatically by email after approval; downloadable from dashboard.",
        "intents": ["vessel_deletion"],
        "related": ["pleasure_boat_renewal", "mortgage_deletion"],
    },
    "port_compliance": {
        "name": "Annual Endorsement of Port Statement of Compliance",
        "name_ar": "التصديق السنوي على بيان امتثال الميناء",
        "category": "Port Services",
        "keywords": [
            "port", "compliance", "endorsement", "annual",
            "statement of compliance", "ميناء", "امتثال", "تصديق",
        ],
        "url": "https://www.moei.gov.ae/en/services/annual-endorsement-of-port-statement-of-compliance",
        "portal_path": "Services Directory → Maritime Transportation → Port Services → Annual Endorsement of Port Statement of Compliance",
        "requires_uae_pass": True,
        "required_info": ["Application information", "Required supporting documents"],
        "delivery": "Email notification on approval; pay fees online; certificate downloadable from dashboard.",
        "intents": ["port_compliance"],
        "related": [],
    },
    "vessel_mortgage": {
        "name": "Application for Mortgage on a National Commercial Vessel",
        "name_ar": "طلب رهن سفينة تجارية وطنية",
        "category": "Commercial Vessel Services",
        "keywords": [
            "mortgage", "commercial vessel", "national vessel",
            "رهن", "سفينة تجارية", "سفينة وطنية",
        ],
        "url": "https://www.moei.gov.ae/en/services/application-for-mortgage-on-a-national-commercial-vessel",
        "portal_path": "Services Directory → Maritime Transportation → Commercial Vessel Services → Mortgage Application",
        "requires_uae_pass": True,
        "required_info": ["Application information", "Required supporting documents"],
        "delivery": "Email notification on approval; pay fees online; certificates downloadable from dashboard.",
        "intents": ["vessel_mortgage", "vessel_registration"],
        "related": ["mortgage_deletion"],
    },
    "coc": {
        "name": "Apply for Certificate of Competency (CoC)",
        "name_ar": "التقدم بطلب شهادة الكفاءة",
        "category": "Seamen Affairs Services",
        "keywords": [
            "coc", "certificate of competency", "seafarer", "seaman",
            "maritime certificate", "شهادة الكفاءة", "بحار", "ملاح",
        ],
        "url": "https://www.moei.gov.ae/en/services/apply-for-certificate-of-competency-coc",
        "portal_path": "Services Directory → Maritime Transportation → Seamen Affairs Services → Certificate of Competency",
        "requires_uae_pass": True,
        "required_info": ["Application information"],
        "delivery": "Certificate issued automatically by email after approval; downloadable from dashboard.",
        "intents": ["license_inquiry", "seafarer"],
        "related": ["coc_reissue", "flag_state_endorsement"],
    },
    "flag_state_endorsement": {
        "name": "Apply for Flag State Endorsement",
        "name_ar": "التقدم بطلب تأييد دولة العلم",
        "category": "Seamen Affairs Services",
        "keywords": [
            "flag state", "endorsement", "seafarer", "flag",
            "تأييد", "دولة العلم", "بحار",
        ],
        "url": "https://www.moei.gov.ae/en/services/apply-for-flag-state-endorsement",
        "portal_path": "Services Directory → Maritime Transportation → Seamen Affairs Services → Flag State Endorsement",
        "requires_uae_pass": True,
        "required_info": ["Application information", "Required supporting documents"],
        "delivery": "Email notification on approval; pay fees online; certificate downloadable.",
        "intents": ["seafarer", "license_inquiry"],
        "related": ["coc", "gmdss"],
    },
    "gmdss": {
        "name": "Apply for GMDSS Endorsement",
        "name_ar": "التقدم بطلب تأييد GMDSS",
        "category": "Seamen Affairs Services",
        "keywords": [
            "gmdss", "global maritime distress", "safety system",
            "radio", "distress", "تأييد GMDSS",
        ],
        "url": "https://www.moei.gov.ae/en/services/apply-for-gmdss-endorsement",
        "portal_path": "Services Directory → Maritime Transportation → Seamen Affairs Services → GMDSS Endorsement",
        "requires_uae_pass": True,
        "required_info": ["Application information", "Required supporting documents"],
        "delivery": "Email notification on approval; pay fees online; certificate downloadable.",
        "intents": ["seafarer"],
        "related": ["flag_state_endorsement", "coc"],
    },
    "coc_reissue": {
        "name": "Re-issue of Certificate of Competency (CoC) — Damaged or Lost",
        "name_ar": "إعادة إصدار شهادة الكفاءة (تالفة أو مفقودة)",
        "category": "Seamen Affairs Services",
        "keywords": [
            "reissue", "re-issue", "lost", "damaged", "replace",
            "coc", "certificate", "فقدان", "تلف", "إعادة إصدار",
        ],
        "url": "https://www.moei.gov.ae/en/services/request-for-replacement-for-a-damaged-lost-certificate-of-competency-and-endorsement",
        "portal_path": "Services Directory → Maritime Transportation → Seamen Affairs Services → Re-issue CoC",
        "requires_uae_pass": True,
        "required_info": ["Application information", "Required supporting documents"],
        "delivery": "Email notification on approval; pay fees online; certificate downloadable.",
        "intents": ["license_inquiry", "seafarer"],
        "related": ["coc", "flag_state_endorsement"],
    },
    "mortgage_deletion": {
        "name": "Deleting Mortgage on Pleasure Boat",
        "name_ar": "شطب الرهن على قارب النزهة",
        "category": "Pleasure Boat Services",
        "keywords": [
            "delete mortgage", "mortgage deletion", "remove mortgage",
            "pleasure boat", "شطب رهن", "قارب", "حذف رهن",
        ],
        "url": "https://www.moei.gov.ae/en/services/deleting-mortgage-pleasure-boat",
        "portal_path": "Services Directory → Maritime Transportation → Pleasure Boat Services → Deleting Mortgage",
        "requires_uae_pass": True,
        "required_info": ["Application information", "Required supporting documents"],
        "delivery": "Email notification on approval; pay fees online.",
        "intents": ["vessel_mortgage"],
        "related": ["vessel_mortgage", "pleasure_boat_deletion"],
    },
    "pro_card": {
        "name": "Issuing a PRO Card",
        "name_ar": "إصدار بطاقة المهنيين (PRO)",
        "category": "Seamen Affairs Services",
        "keywords": [
            "pro card", "pro", "professional card", "seafarer card",
            "بطاقة PRO", "بطاقة مهنية", "بطاقة البحار",
        ],
        "url": "https://www.moei.gov.ae/en/services/issuing-a-pro-card",
        "portal_path": "Services Directory → Maritime Transportation → Seamen Affairs Services → PRO Card",
        "requires_uae_pass": True,
        "required_info": ["Application information", "Required supporting documents"],
        "delivery": "Email notification on approval; pay fees online; card downloadable.",
        "intents": ["seafarer"],
        "related": ["coc", "flag_state_endorsement"],
    },
}

FALLBACK_URL = "https://www.moei.gov.ae/en/services/maritime-transport/"


def find_service(query: str = "", intent: str = "") -> dict | None:
    """Return the best matching service for a query or intent string."""
    query_lower = query.lower()
    best_score = 0
    best_service = None

    for service in SERVICES.values():
        score = 0
        # Intent match (highest weight)
        if intent and intent in service.get("intents", []):
            score += 10
        # Keyword overlap
        for kw in service["keywords"]:
            if kw.lower() in query_lower:
                score += 2
        if score > best_score:
            best_score = score
            best_service = service

    return best_service if best_score > 0 else None


def catalog_summary() -> str:
    """One-line summary of each service for system prompt context."""
    return "\n".join(
        f"- {s['name']} | {s['name_ar']} | {s['portal_path']}"
        for s in SERVICES.values()
    )
