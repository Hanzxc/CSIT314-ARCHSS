# Control: ViewIDPController - UC32 View IDP (US32)
# precondition: the customer is already logged in (US30), so there's no access check here.
# the designer's company profile is US15's job - the page borrows that controller

from entity.idp import IDP


class ViewIDPController:
    # UC32 View IDP
    # the IDP if customers can see it, else None. countView says if this opening counts as a view
    def viewIDP(self, idpId, countView):
        return IDP().viewIDP(idpId, countView)
