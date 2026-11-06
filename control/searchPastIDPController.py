# Control: SearchPastIDPController - UC29 Search past IDPs (US29)

from entity.idp import IDP


class SearchPastIDPController:
    # UC29 Search past IDPs
    # the page has already checked the keyword - this just asks the entity
    def searchPastIDPs(self, designerId, keyword):
        return IDP().searchByKeywordAndDesigner(keyword, designerId)
