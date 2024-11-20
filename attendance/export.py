from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

@dataclass
class ExportConfig:
    """Configuration for data export"""
    include_headers: bool = True
    date_format: str = "%Y-%m-%d %H:%M:%S"
    custom_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None
    field_mapping: Optional[Dict[str, str]] = None

class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    RAW = "raw"  # Returns formatted data without file generation

class ExportService:
    def format_data(
        self,
        data: List[Dict[str, Any]],
        config: Optional[ExportConfig] = None
    ) -> Dict[str, Any]:
        """Format data according to configuration"""
        if config is None:
            config = ExportConfig()

        if not data:
            return {
                "headers": [],
                "rows": [],
                "metadata": {
                    "total_records": 0,
                    "exported_at": datetime.utcnow().isoformat()
                }
            }

        # Get fields based on configuration
        fields = self._get_fields(data[0], config)
        headers = self._get_headers(fields, config.field_mapping)

        # Process rows
        rows = [
            self._process_row(row, fields, config)
            for row in data
        ]

        return {
            "headers": headers,
            "rows": rows,
            "metadata": {
                "total_records": len(rows),
                "exported_at": datetime.utcnow().isoformat(),
                "config": {
                    "date_format": config.date_format,
                    "included_fields": fields
                }
            }
        }

    def _get_fields(self, sample_data: Dict[str, Any], config: ExportConfig) -> List[str]:
        """Get fields to export based on configuration"""
        if config.custom_fields:
            return config.custom_fields

        fields = list(sample_data.keys())
        if config.exclude_fields:
            fields = [f for f in fields if f not in config.exclude_fields]
        return fields

    def _get_headers(self, fields: List[str], field_mapping: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Get headers with optional field mapping"""
        if field_mapping:
            return {field: field_mapping.get(field, field) for field in fields}
        return {field: field for field in fields}

    def _process_row(self, row: Dict[str, Any], fields: List[str], config: ExportConfig) -> Dict[str, Any]:
        """Process a single row of data"""
        processed_row = {}
        for field in fields:
            value = row.get(field)
            if isinstance(value, datetime):
                processed_row[field] = value.strftime(config.date_format)
            else:
                processed_row[field] = value
        return processed_row

    def format_attendance_data(
        self,
        attendance_records: List[Dict[str, Any]],
        include_student_info: bool = True,
        include_class_info: bool = True
    ) -> Dict[str, Any]:
        """
        Special formatter for attendance data with customizable includes
        """
        config = ExportConfig(
            field_mapping={
                "student_id": "Student ID",
                "student_name": "Student Name",
                "class_name": "Class",
                "status": "Attendance Status",
                "recorded_at": "Time",
                "verification_method": "Verification Method"
            }
        )

        # Customize fields based on includes
        exclude_fields = []
        if not include_student_info:
            exclude_fields.extend(["student_details", "student_email"])
        if not include_class_info:
            exclude_fields.extend(["class_details", "teacher_name"])

        config.exclude_fields = exclude_fields

        return self.format_data(attendance_records, config)

# Global export service instance
export_service = ExportService() 