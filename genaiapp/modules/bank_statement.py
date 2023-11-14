import os
import uuid
import shutil
import pandas as pd
from genaiapp.modules.utils.bank_statement_helper import BCA_extraction, CIMB_extraction, BRI_extraction

class BankStatementProcessor:
    def __init__(self, bank_name):
        self.bank_name = bank_name

    @staticmethod
    def upload_files(file_path):
        file_paths = file_path.split(",")
        uploaded_files = []
        for path in file_paths:
            with open(path, 'rb') as file:
                uploaded_files.append({'name': os.path.basename(path), 'content': file.read()})
        return uploaded_files

    def process_files(self, uploaded_files):
        foldername = self.bank_name + str(uuid.uuid4())
        os.mkdir(foldername)
        for uploaded_file in uploaded_files:
            with open(os.path.join(foldername, uploaded_file['name']), "wb") as temp_file:
                temp_file.write(uploaded_file['content'])

        # Initialize all result variables with default values
        data_result = None
        prefix = None
        TransactionDetail = None
        TransactionDetail2 = None
        sufix = None

        if self.bank_name == "BCA":
            data_result, prefix, TransactionDetail, TransactionDetail2, sufix = BCA_extraction(foldername)
        elif self.bank_name == "CIMB":
            data_result, prefix, TransactionDetail, sufix = CIMB_extraction(foldername)
        elif self.bank_name == "BRI":
            data_result, prefix, TransactionDetail, sufix = BRI_extraction(foldername)

        shutil.rmtree(foldername)
        nan_placeholder = "NaN"
        transaction_detail = ()
        if self.bank_name == "BCA":
            if TransactionDetail2 is not None and not TransactionDetail2.empty:
                if 'TANGGAL' in TransactionDetail2.columns:
                    TransactionDetail2['TANGGAL'] = pd.to_datetime(TransactionDetail2['TANGGAL'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
                # Replace NaN values with the placeholder string
                TransactionDetail2.fillna(nan_placeholder, inplace=True)
                for _, row in TransactionDetail2.iterrows():
                    # Convert each row to a dictionary
                    row_dict = {col: row[col] for col in TransactionDetail2.columns}
                    # Add this dictionary to the tuple
                    transaction_detail += (row_dict,)
        else:
            if TransactionDetail is not None and not TransactionDetail.empty:
                # Replace NaN values with the placeholder string
                TransactionDetail.fillna(nan_placeholder, inplace=True)
                for _, row in TransactionDetail.iterrows():
                    # Convert each row to a dictionary
                    row_dict = {col: row[col] for col in TransactionDetail.columns}
                    # Add this dictionary to the tuple
                    transaction_detail += (row_dict,)

        transaction_analysis = ()
        if data_result.get("Transaction_Analysis") is not None and not data_result.get("Transaction_Analysis").empty:
            for _, row in data_result.get("Transaction_Analysis").iterrows():
                # Convert each row to a dictionary
                row_dict = {col: row[col] for col in data_result.get("Transaction_Analysis").columns}
                # Add this dictionary to the tuple
                transaction_analysis += (row_dict,)

        # Assign the tuple of dictionaries to "table" in ocr_result
        ocr_result = {"prefix": prefix, "sufix": sufix, "table": transaction_detail}
        extraction_result = {"bank_name": ""+self.bank_name+"", "account_number": data_result.get('Account_Number'), "account_holder": data_result.get('Account_Holder'), "table": transaction_analysis}
        free_prompt = {"table":transaction_detail, "prefix_ocr":prefix, "prompt_dataframe": "prompt data frame"}

        # You may return or handle ocr_result as needed
        # return ocr_result
        return data_result, prefix, TransactionDetail, TransactionDetail2, sufix, ocr_result, extraction_result

    @staticmethod
    def print_data(data):
        if data is not None:
            if isinstance(data, pd.DataFrame):
                if not data.empty:
                    print(data)
                else:
                    print("DataFrame is empty.")
            elif isinstance(data, dict):
                for key, value in data.items():
                    print(f"{key}: {value}")
            else:
                print("Unsupported data type.")
        else:
            print("No data available.")

BankStatementProcessor