
class ReceiptController:
    def __init__(self, boto3_session):
        self.boto3_session = boto3_session
        self.receipt = dict()

    def read_receipt_from_aws(self, boto3_session):
        return NotImplementedError()

    def write_receipt_to_aws(self, boto3_session):
        return NotImplementedError()

    def get_receipt(self):
        return NotImplementedError()

    def generate_sdk(self):
        return NotImplementedError()