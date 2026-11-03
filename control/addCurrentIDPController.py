# Control: AddCurrentIDPController - UC20 Add current IDP (US20)

from entity.idp import IDP


class AddCurrentIDPController:
    # UC20 Add current IDP
    # the page checks the input, the entity checks the category is still Active - this just calls add
    def addCurrentIDP(self, idp):
        return IDP().addCurrentIDP(idp)
