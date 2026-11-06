# Control: AddPastIDPController - UC25 Add past IDP (US25)

from entity.idp import IDP


class AddPastIDPController:
    # UC25 Add past IDP
    # the page checks the input, the entity checks the category is still Active - this just calls create
    def addPastIDP(self, idp):
        return IDP().createPastIDP(idp)
