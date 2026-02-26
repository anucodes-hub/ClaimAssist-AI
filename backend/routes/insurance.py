from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

insurance_bp = Blueprint('insurance', __name__)

INSURANCE_CHECKLISTS = {
    "health": {
        "name": "Health Insurance",
        "icon": "🏥",
        "documents": [
            {"id": "discharge_summary", "label": "Hospital Discharge Summary", "required": True},
            {"id": "prescription", "label": "Doctor's Prescription", "required": True},
            {"id": "bills", "label": "Original Hospital Bills & Receipts", "required": True},
            {"id": "lab_reports", "label": "Laboratory / Diagnostic Reports", "required": True},
            {"id": "id_proof", "label": "Photo ID Proof (Aadhaar/PAN)", "required": True},
            {"id": "policy_doc", "label": "Insurance Policy Document", "required": True},
            {"id": "referral", "label": "Doctor's Referral Letter", "required": False},
            {"id": "prev_records", "label": "Previous Medical Records", "required": False},
        ],
        "validation_rules": ["admission_date", "discharge_date", "claim_amount", "patient_name"]
    },
    "life": {
        "name": "Life Insurance",
        "icon": "💼",
        "documents": [
            {"id": "death_certificate", "label": "Original Death Certificate", "required": True},
            {"id": "policy_doc", "label": "Original Insurance Policy", "required": True},
            {"id": "id_proof", "label": "Nominee's Photo ID", "required": True},
            {"id": "bank_details", "label": "Bank Account Details (Cancelled Cheque)", "required": True},
            {"id": "claim_form", "label": "Duly Filled Claim Form", "required": True},
            {"id": "fir", "label": "FIR (In case of accidental death)", "required": False},
            {"id": "post_mortem", "label": "Post Mortem Report (If applicable)", "required": False},
        ],
        "validation_rules": ["date_of_death", "policy_number", "nominee_name"]
    },
    "vehicle": {
        "name": "Vehicle Insurance",
        "icon": "🚗",
        "documents": [
            {"id": "fir", "label": "FIR Copy (Police Report)", "required": True},
            {"id": "rc_book", "label": "Vehicle Registration Certificate (RC)", "required": True},
            {"id": "driving_license", "label": "Valid Driving License", "required": True},
            {"id": "policy_doc", "label": "Insurance Policy Document", "required": True},
            {"id": "repair_bills", "label": "Vehicle Repair Bills / Estimate", "required": True},
            {"id": "photos", "label": "Accident/Damage Photographs", "required": True},
            {"id": "id_proof", "label": "Owner's Photo ID", "required": True},
        ],
        "validation_rules": ["accident_date", "vehicle_number", "damage_description"]
    },
    "travel": {
        "name": "Travel Insurance",
        "icon": "✈️",
        "documents": [
            {"id": "passport", "label": "Passport Copy", "required": True},
            {"id": "ticket", "label": "Travel Tickets / Boarding Pass", "required": True},
            {"id": "policy_doc", "label": "Travel Insurance Policy", "required": True},
            {"id": "medical_bills", "label": "Medical Bills (if medical claim)", "required": False},
            {"id": "pir", "label": "Property Irregularity Report (Baggage loss)", "required": False},
            {"id": "hotel_bills", "label": "Hotel/Accommodation Bills", "required": False},
            {"id": "cancellation_proof", "label": "Trip Cancellation Proof", "required": False},
        ],
        "validation_rules": ["travel_date", "return_date", "destination"]
    },
    "property": {
        "name": "Property Insurance",
        "icon": "🏠",
        "documents": [
            {"id": "ownership_proof", "label": "Property Ownership Documents", "required": True},
            {"id": "fir", "label": "FIR / Police Report", "required": True},
            {"id": "policy_doc", "label": "Insurance Policy", "required": True},
            {"id": "damage_photos", "label": "Photographs of Damage", "required": True},
            {"id": "repair_estimate", "label": "Repair Cost Estimate", "required": True},
            {"id": "id_proof", "label": "Owner's Photo ID", "required": True},
            {"id": "valuation_report", "label": "Property Valuation Report", "required": False},
        ],
        "validation_rules": ["incident_date", "property_address", "damage_amount"]
    }
}

@insurance_bp.route('/types', methods=['GET'])
@jwt_required()
def get_insurance_types():
    types = [
        {"id": k, "name": v["name"], "icon": v["icon"]} 
        for k, v in INSURANCE_CHECKLISTS.items()
    ]
    return jsonify({"types": types})

@insurance_bp.route('/checklist/<insurance_type>', methods=['GET'])
@jwt_required()
def get_checklist(insurance_type):
    if insurance_type not in INSURANCE_CHECKLISTS:
        return jsonify({'error': 'Invalid insurance type'}), 404
    
    checklist = INSURANCE_CHECKLISTS[insurance_type]
    return jsonify({
        "insurance_type": insurance_type,
        "name": checklist["name"],
        "documents": checklist["documents"],
        "validation_rules": checklist["validation_rules"]
    })