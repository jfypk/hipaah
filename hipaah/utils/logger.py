import datetime
import json
import os
from typing import Dict, Any, Optional, Set

class SafeLogger:
    """
    SafeLogger provides logging utilities that automatically mask sensitive PHI fields.
    It supports logging to console and optionally to files for audit purposes.
    """
    
    def __init__(self, masked_fields=None, log_file_path=None, justification_log_path=None):
        """
        Initialize the SafeLogger.
        
        Args:
            masked_fields: Set of field names to mask in logs
            log_file_path: Optional path to write logs to a file
            justification_log_path: Optional path to write justification logs
        """
        self.masked_fields = set(masked_fields or [])
        self.log_file_path = log_file_path
        
        # Default justification log path if not provided
        if log_file_path and not justification_log_path:
            dir_path = os.path.dirname(log_file_path)
            self.justification_log_path = os.path.join(dir_path, "justification_log.jsonl")
        else:
            self.justification_log_path = justification_log_path

    def redact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact sensitive fields from data.
        
        Args:
            data: Dictionary of data to redact
            
        Returns:
            Redacted data with sensitive fields masked
        """
        if not data:
            return {}
            
        return {k: "***" if k in self.masked_fields else v for k, v in data.items()}

    def info(self, message: str, data: Dict[str, Any] = None):
        """
        Log an informational message with optional data.
        
        Args:
            message: The message to log
            data: Optional data to include in the log, will be redacted
        """
        self._log("INFO", message, data or {})
        
    def warning(self, message: str, data: Dict[str, Any] = None):
        """
        Log a warning message with optional data.
        
        Args:
            message: The warning message to log
            data: Optional data to include in the log, will be redacted
        """
        self._log("WARNING", message, data or {})
        
    def error(self, message: str, data: Dict[str, Any] = None):
        """
        Log an error message with optional data.
        
        Args:
            message: The error message to log
            data: Optional data to include in the log, will be redacted
        """
        self._log("ERROR", message, data or {})
        
    def justification(self, role: str, intent: str, resource_id: str, justification: str, expires_at: Optional[str] = None):
        """
        Log a justification entry for accessing PHI.
        
        Args:
            role: The role accessing the data
            intent: The intent of the access
            resource_id: Identifier for the resource
            justification: Reason for the access
            expires_at: Optional ISO formatted datetime string when access expires
        """
        # Create the justification data
        justification_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "role": role,
            "intent": intent,
            "resource_id": resource_id,
            "justification": justification
        }
        
        # Add expiry if provided
        if expires_at:
            justification_data["expires_at"] = expires_at
            
        # Write to the justification log if path provided
        if self.justification_log_path:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.justification_log_path), exist_ok=True)
                
                with open(self.justification_log_path, "a") as f:
                    f.write(json.dumps(justification_data) + "\n")
            except Exception as e:
                self.error(f"Failed to write to justification log: {str(e)}")
                
        # Also log a regular info message
        self.info(f"Access justified by {role} for {intent}", {
            "resource_id": resource_id,
            "has_expiry": expires_at is not None
        })
    
    def _log(self, level: str, message: str, data: Dict[str, Any]):
        """
        Internal method to log a message with data.
        
        Args:
            level: Log level (INFO, WARNING, ERROR)
            message: The message to log
            data: Data to include in the log, will be redacted
        """
        timestamp = datetime.datetime.now().isoformat()
        redacted = self.redact(data)
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "data": redacted
        }
        
        # Print to console
        print(f"[{level}] {message} {redacted}")
        
        # Write to file if path provided
        if self.log_file_path:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
                
                with open(self.log_file_path, "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception as e:
                print(f"[ERROR] Failed to write to log file: {str(e)}")
