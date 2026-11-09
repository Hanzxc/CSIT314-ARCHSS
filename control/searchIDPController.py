# Control: SearchIDPController - UC31 Search IDPs (US31)
# precondition: the customer is already logged in (US30), so there's no access check here

from entity.idp import IDP


class SearchIDPController:
    # UC31 Search IDPs
    # the page has already trimmed the keyword - this just passes it on
    def searchIDPs(self, keyword):
        return IDP().searchIDPs(keyword)
