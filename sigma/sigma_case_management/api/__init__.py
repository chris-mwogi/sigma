# Case Management API Module
# Exposes all case management, evidence, IoT, communication, and reporting endpoints

from .case_management_api import (
    create_case,
    assign_case,
    update_case_status,
    escalate_case,
    close_case,
    reopen_case
)

from .evidence_api import (
    add_evidence,
    get_evidence,
    verify_evidence_integrity,
    add_custody_entry,
    get_evidence_chain_of_custody,
    scan_evidence_for_virus,
    export_evidence_metadata
)



from .communication_api import (
    add_comment,
    log_communication,
    get_case_discussions,
    get_case_communications,
    pin_discussion,
    mark_communication_resolved
)

from .reporting_api import (
    get_investigator_workload,
    get_case_timeline,
    get_cases_by_status,
    get_sla_metrics,
    get_asset_theft_report,
    export_case_for_legal
)

__all__ = [
    # Case Management
    'create_case',
    'assign_case',
    'update_case_status',
    'escalate_case',
    'close_case',
    'reopen_case',
    
    # Evidence Management
    'add_evidence',
    'get_evidence',
    'verify_evidence_integrity',
    'add_custody_entry',
    'get_evidence_chain_of_custody',
    'scan_evidence_for_virus',
    'export_evidence_metadata',

    # Communication
    'add_comment',
    'log_communication',
    'get_case_discussions',
    'get_case_communications',
    'pin_discussion',
    'mark_communication_resolved',
    
    # Reporting
    'get_investigator_workload',
    'get_case_timeline',
    'get_cases_by_status',
    'get_sla_metrics',
    'get_asset_theft_report',
    'export_case_for_legal'
]

