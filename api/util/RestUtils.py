
class RestUtils:
    """
    @author harrisonkelly

    Utility functions for the REST api.
    """

    @staticmethod
    def generateInventoryEntry(barcode, addedDate):
        """
        Generates a JSON entry for the inventory.
        """
        entry = ""

        if (barcode != "" and addedDate != ""):
            entry = "    \"barcode\": \"" + barcode + "\",\n"
            entry += "    \"expirationdate\": \"\",\n"
            entry += "    \"added\": \"" + addedDate + "\"\n}]"

            return entry
