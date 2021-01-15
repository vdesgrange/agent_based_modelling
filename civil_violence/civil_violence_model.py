from mesa import Model


class CivilViolenceModel(Model):
    """
    Civil violence model
    """
    def __init__(self, height=40, width=40):
        super().__init__()
        self.height = height
        self.width = width
