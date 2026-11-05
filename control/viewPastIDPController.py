from entity.idp import IDP

class ViewPastIDPsController:
    def __init__(self):
        self.idp_entity = IDP()

    def getPastIDPsByDesigner(self, designer_id):
        if not designer_id:
            return []
        return self.idp_entity.getPastIDPsByDesigner(designer_id)