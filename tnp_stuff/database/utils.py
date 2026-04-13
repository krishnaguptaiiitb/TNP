import re

pattern_regex = {
    'scholar_no' : re.compile(r'^(0[1-9]|[1-9]\d)U(0[1-9]|[1-9]\d)(\d)?(00[1-9]|0[1-9]\d|[1-9]\d{2})$|^(0[1-9]|[1-9]\d)P(0[1-9]|[1-9]\d)(P|F)?(\d)?(00[1-9]|0[1-9]\d|[1-9]\d{2})$'),
    'name': re.compile(r'^[a-zA-Z\s]{1,50}$'),
    'graduation_year': re.compile(r'^(19|20)\d{2}$'),
    'mail_id': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    'phone_no': re.compile(r'^\+?[1-9]\d{1,14}$'),
    'branch_id': re.compile(r'^[A-Z]{2,5}$'),
    'program': re.compile(r'^(B\.Tech|M\.Tech|Ph\.D|MBA|MCA)$'),
    'placement_active': re.compile(r'^(active|inactive)$'),
    'internship_active': re.compile(r'^(active|inactive)$'),
    'type' : re.compile(r'(entry|upload)$'),
    'company_id' : re.compile(r'^[1-9][0-9]*$'),
    'company_name' : re.compile(r'^[a-zA-Z0-9\s]{1,50}$'),
    'posts' : re.compile(r'^[a-zA-Z0-9\s,]{1,100}$'),
    'job_type' : re.compile(r'^(Full_Time|Internship|Both)$'),
    'ctc_min' : re.compile(r'^\d+(\.\d{1,2})?$'),
    'ctc_max' : re.compile(r'^\d+(\.\d{1,2})?$'),
    'applied_students' : re.compile(r'^[0-9]\d*$'),
    'selected_students' : re.compile(r'^[0-9]\d*$'),
    'visit_date' : re.compile(r'^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'),
    'location' : re.compile(r'^(Onsite|Remote|Hybrid)$'),
    'status' : re.compile(r'^(Visited|Upcoming|Rejected|Pending)$'),
    'placement_status' : re.compile(r'^(Applied|Selected|Rejected)$'),
    'package' : re.compile(r'^\d+(\.\d{1,2})?$'),
    'offer_date' : re.compile(r'^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'),
    'entry_id' : re.compile(r'^[1-9]\d*$')
}

def evaluate_expression(field, last_status, last_message, current_string, pattern_machine):
    if last_status is False:
        return (last_status, last_message, None)
    
    if current_string is None:
        return (False, f"Invalid Input: missing {field}", None)

    try:
        if re.fullmatch(pattern_machine, str(current_string)):
            return (True, "Valid Input", current_string)
        else:
            return (False, f"Invalid Input: {current_string}", None)
    except Exception as e:
        return (False, f"field : {current_string} , error : {str(e)}", None)
