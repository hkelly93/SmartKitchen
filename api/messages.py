
class Messages:
    """
    @author harrisonkelly

    Used for the possibility of localization.
    """
    @staticmethod
    def inventoryNotFound():
        return "Error finding the inventory. Please make sure that the network status is healthy."

    @staticmethod
    def barcodeNotFound(barcode):
        return "Error finding " + str(barcode) + "in inventory"
