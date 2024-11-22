from datetime import datetime
import json
import platform


class ProcessingLogger:
    def __init__(self, storage_manager, metadata_prefix):
        self.storage = storage_manager
        self.metadata_prefix = metadata_prefix
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.logs = {
            "date": self.current_date,
            "system_info": {
                "platform": platform.system(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            },
            "files_processed": 0,
            "successful": 0,
            "failed": 0,
            "total_saved_space": 0,
            "processing_details": []
        }

    def log_conversion(self, video_path, success, processing_time, details=None, error=None):
        log_entry = {
            "file": video_path,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "success": success,
            "processing_time_seconds": processing_time
        }

        if success and details:
            log_entry.update({
                "input_size": details['input_size'],
                "output_size": details['output_size'],
                "size_reduction_percent": details['reduction'],
                "input_bitrate": details['input_bitrate'],
                "target_bitrate": details['target_bitrate']
            })
            self.logs["total_saved_space"] += (details['input_size'] - details['output_size'])
            self.logs["successful"] += 1
        else:
            log_entry["error"] = str(error)
            self.logs["failed"] += 1

        self.logs["files_processed"] += 1
        self.logs["processing_details"].append(log_entry)

    def save_logs(self):
        # Save daily log
        daily_log_path = f"{self.metadata_prefix}logs/{self.current_date}_processing_log.json"
        self.storage.save_metadata(self.logs, daily_log_path)

        try:
            stats = self.storage.get_processed_files(f"{self.metadata_prefix}stats.json")
            stats["total_processed"] = stats.get("total_processed", 0) + self.logs["files_processed"]
            stats["total_successful"] = stats.get("total_successful", 0) + self.logs["successful"]
            stats["total_failed"] = stats.get("total_failed", 0) + self.logs["failed"]
            stats["total_saved_space"] = stats.get("total_saved_space", 0) + self.logs["total_saved_space"]
            stats["last_update"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.storage.save_metadata(stats, f"{self.metadata_prefix}stats.json")
        except Exception as e:
            print(f"Error updating cumulative stats: {e}")