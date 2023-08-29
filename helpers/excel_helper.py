import xlsxwriter
import os

from datetime import datetime
from utils.file_utils import check_directory_exist


class ExcelHelper:
    def __init__(self, file_name: str) -> None:
        self.output_folder = self._generate_unique_folder()
        self.file_name = os.path.join(self.output_folder, file_name)

    def write(self, excel_data: list) -> None:
        """Write data to excel file."""
        workbook = xlsxwriter.Workbook(self.file_name)
        for data in excel_data:
            worksheet = workbook.add_worksheet()
            row = 0
            col = 0
            for field, value in data.items():
                if self._is_image_field(field):
                    if value:
                        worksheet.insert_image(row, col + 1, value)
                else:
                    worksheet.write(row, col, field)
                    worksheet.write(row, col + 1, value)
                row += 1
        workbook.close()

    @staticmethod
    def _is_image_field(field_name):
        return field_name in ("image_path",)

    def _generate_unique_folder(self):
        now = datetime.now()
        now_timestamp = int(datetime.timestamp(now))
        folder_path = os.path.join("output", str(now_timestamp))
        check_directory_exist(folder_path)
        return folder_path
