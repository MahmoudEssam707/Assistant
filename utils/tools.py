"""Tool definitions using @tool decorator for the agent."""

from .util import logger
from langchain_core.tools import tool
from langchain_google_community.gmail.send_message import GmailSendMessage
from langchain_google_community.gmail.utils import (
    build_gmail_service,
    get_google_credentials,
)
from googleapiclient.discovery import build

try:
    credentials = get_google_credentials(
        token_file="token.json",
        scopes=[
            "https://mail.google.com/",  # Gmail scope
            "https://www.googleapis.com/auth/spreadsheets"  # Sheets scope
        ],
        client_secrets_file="credentials.json",
    )
    api_resource = build_gmail_service(credentials=credentials)
    send_mail_tool = GmailSendMessage.from_api_resource(api_resource=api_resource)
    sheets_service = build('sheets', 'v4', credentials=credentials)
except:
    api_resource = None
    send_mail_tool = None
    sheets_service = None

@tool
def calculator_tool(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    
    Args:
        expression: The mathematical expression to evaluate (e.g., "4*4", "10+5")
        
    Returns:
        The result of the calculation as a string
    """
    logger.info(f"Calculator tool executing: {expression}")
    try:
        result = eval(expression)
        logger.info(f"Calculator result: {result}")
        return str(result)
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return "Invalid mathematical expression"


@tool
def sheet_crud_tool(
    sheet_id: str, 
    operation: str, 
    data: str = "", 
    sheet_name: str = "Sheet1"
) -> str:
    """
    Unified CRUD tool for Google Sheets operations.
    
    Args:
        sheet_id: The ID of the Google Sheet
        operation: Operation type - 'create', 'read', 'update', 'delete', 'info'
        data: Data string formatted based on operation:
            - create: "ID - COL1 - COL2\\n123 val1 val2\\n456 val3 val4"
            - read: "10" (number of records) or empty for all
            - update: "ID : COL1\\n123 : newvalue"
            - delete: "ID\\n123" (identifier to delete)
            - info: empty (returns sheet info)
        sheet_name: Sheet tab name (default: "Sheet1")
        
    Returns:
        Result message based on operation
    """
    if not sheets_service:
        return "Error: Google Sheets service not available"
    
    try:
        # INFO - Get sheet information
        if operation == "info":
            spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            title = spreadsheet['properties']['title']
            sheet_names = [s['properties']['title'] for s in spreadsheet['sheets']]
            return f"Title: {title}\nSheets: {', '.join(sheet_names)}\nURL: https://docs.google.com/spreadsheets/d/{sheet_id}"
        
        # READ - Get records
        elif operation == "read":
            limit = int(data) if data.strip().isdigit() else 10
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id, 
                range=f'{sheet_name}!A1:Z{limit + 1}'
            ).execute()
            values = result.get('values', [])
            
            if not values:
                return "No data found in the sheet"
            
            if len(values) == 1:
                return f"Sheet only contains headers: {', '.join(values[0])}"
            
            headers = values[0]
            data_rows = values[1:]
            
            output = f"Top {len(data_rows)} records from '{sheet_name}':\n\n"
            output += "Headers: " + ", ".join(headers) + "\n\n"
            
            for idx, row in enumerate(data_rows, 1):
                padded_row = row + [''] * (len(headers) - len(row))
                row_str = ", ".join(f"{headers[i]}: {padded_row[i]}" for i in range(len(headers)))
                output += f"Row {idx}: {row_str}\n"
            
            output += f"\nTotal records: {len(data_rows)}\n"
            output += f"Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}"
            return output
        
        # CREATE - Add new records
        elif operation == "create":
            lines = [line.strip() for line in data.split('\n') if line.strip()]
            
            if len(lines) < 2:
                return "Error: Need at least column names and one row of data"
            
            # Parse column names from first line (format: ID - COL1 - COL2)
            columns = [col.strip() for col in lines[0].split('-')]
            
            if len(columns) < 2:
                return "Error: Need at least 2 columns"
            
            # Get existing headers
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f'{sheet_name}!1:1').execute()
            headers = result.get('values', [[]])[0]
            
            # Add missing columns
            columns_added = []
            for col_name in columns:
                if not any(col_name.lower() in h.lower() for h in headers):
                    next_col = chr(ord('A') + len(headers))
                    sheets_service.spreadsheets().values().update(
                        spreadsheetId=sheet_id,
                        range=f'{sheet_name}!{next_col}1',
                        valueInputOption='RAW',
                        body={'values': [[col_name]]}
                    ).execute()
                    headers.append(col_name)
                    columns_added.append(col_name)
            
            # Map columns to indices
            col_indices = {}
            for col_name in columns:
                for idx, header in enumerate(headers):
                    if col_name.lower() in header.lower():
                        col_indices[col_name] = idx
                        break
            
            # Get current row count
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f'{sheet_name}!A:A').execute()
            current_rows = len(result.get('values', []))
            next_row = current_rows + 1
            
            # Add data rows
            rows_added = 0
            for line_idx in range(1, len(lines)):
                row_data = lines[line_idx].split()
                
                if len(row_data) != len(columns):
                    continue
                
                full_row = [''] * len(headers)
                for col_idx, value in enumerate(row_data):
                    col_name = columns[col_idx]
                    if col_name in col_indices:
                        full_row[col_indices[col_name]] = value
                
                range_to_update = f'{sheet_name}!A{next_row}:{chr(ord("A") + len(headers) - 1)}{next_row}'
                sheets_service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range=range_to_update,
                    valueInputOption='RAW',
                    body={'values': [full_row]}
                ).execute()
                
                rows_added += 1
                next_row += 1
            
            result_msg = f"Successfully added {rows_added} records"
            if columns_added:
                result_msg += f"\nNew columns created: {', '.join(columns_added)}"
            return result_msg
        
        # UPDATE - Update existing records
        elif operation == "update":
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f'{sheet_name}!A:Z').execute()
            values = result.get('values', [])
            
            if not values:
                return "No data found"
            
            headers, data_rows = values[0], values[1:]
            
            lines = data.strip().split('\n')
            if len(lines) < 2:
                return "Error: Invalid format. Expected: COLUMN1 : COLUMN2\\nVAL1 : VAL2"
            
            columns = [col.strip() for col in lines[0].split(':')]
            values_to_update = [val.strip() for val in lines[1].split(':')]
            
            if len(columns) != len(values_to_update):
                return "Error: Number of columns must match number of values"
            
            if len(columns) < 2:
                return "Error: Need at least 2 columns (identifier + update column)"
            
            identifier_col = columns[0].lower()
            identifier_val = values_to_update[0]
            
            identifier_col_idx = next((i for i, h in enumerate(headers) 
                                      if identifier_col in h.lower()), None)
            
            if identifier_col_idx is None:
                return f"Error: Column '{columns[0]}' not found"
            
            update_results = []
            for row_idx, row_data in enumerate(data_rows):
                if identifier_col_idx < len(row_data):
                    if identifier_val.lower() in str(row_data[identifier_col_idx]).lower():
                        for col_idx in range(1, len(columns)):
                            col_name = columns[col_idx].lower()
                            new_value = values_to_update[col_idx]
                            
                            target_col_idx = next((i for i, h in enumerate(headers) 
                                                  if col_name in h.lower()), None)
                            
                            if target_col_idx is not None:
                                cell_range = f'{sheet_name}!{chr(ord("A") + target_col_idx)}{row_idx + 2}'
                                sheets_service.spreadsheets().values().update(
                                    spreadsheetId=sheet_id, range=cell_range,
                                    valueInputOption='RAW', body={'values': [[new_value]]}).execute()
                                update_results.append(f"Updated row {row_idx + 2}: {columns[col_idx]}={new_value}")
            
            return "\n".join(update_results) if update_results else "No matching rows found"
        
        # DELETE - Delete records
        elif operation == "delete":
            lines = [line.strip() for line in data.split('\n') if line.strip()]
            
            if len(lines) < 2:
                return "Error: Need column name and identifier value"
            
            identifier_col = lines[0].lower()
            identifier_val = lines[1]
            
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f'{sheet_name}!A:Z').execute()
            values = result.get('values', [])
            
            if not values:
                return "No data found"
            
            headers, data_rows = values[0], values[1:]
            
            identifier_col_idx = next((i for i, h in enumerate(headers) 
                                      if identifier_col in h.lower()), None)
            
            if identifier_col_idx is None:
                return f"Error: Column '{identifier_col}' not found"
            
            rows_to_delete = []
            for row_idx, row_data in enumerate(data_rows):
                if identifier_col_idx < len(row_data):
                    if identifier_val.lower() in str(row_data[identifier_col_idx]).lower():
                        rows_to_delete.append(row_idx + 2)  # +2 for header and 1-based index
            
            if not rows_to_delete:
                return "No matching rows found to delete"
            
            # Delete rows in reverse order to maintain indices
            for row_num in sorted(rows_to_delete, reverse=True):
                request = {
                    'deleteDimension': {
                        'range': {
                            'sheetId': 0,
                            'dimension': 'ROWS',
                            'startIndex': row_num - 1,
                            'endIndex': row_num
                        }
                    }
                }
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=sheet_id,
                    body={'requests': [request]}
                ).execute()
            
            return f"Deleted {len(rows_to_delete)} row(s)"
        
        else:
            return f"Error: Unknown operation '{operation}'. Use: create, read, update, delete, info"
    
    except Exception as e:
        return f"Error: {str(e)}"