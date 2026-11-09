# Control: SearchCurrentIDPController - UC24 Search current IDPs (US24)
# precondition: the designer is already logged in (US13), so there's no access check here

from entity.idp import IDP


class SearchCurrentIDPController:
    # UC24 Search current IDPs
    # the page has already trimmed the keyword - this just passes it on
    def searchCurrentIDPs(self, designerId, keyword):
        return IDP().searchCurrentIDPs(designerId, keyword)
