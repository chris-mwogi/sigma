import frappe
import json

def execute():
    try:
        ws = frappe.get_doc('Workspace', 'Sigma Home')
        print(json.dumps({
            'name': ws.name,
            'module': ws.module,
            'content_length': len(ws.content or ''),
            'content_preview': (ws.content or '')[:300],
            'exists': True
        }))
    except frappe.DoesNotExistError:
        print(json.dumps({
            'exists': False,
            'error': 'Sigma Home workspace does not exist in database'
        }))
    except Exception as e:
        print(json.dumps({
            'exists': False,
            'error': str(e)
        }))
