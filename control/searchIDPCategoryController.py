# Control: SearchIDPCategoryController - UC45 Search IDP categories (US45)

from control.platformManagerLoginController import PlatformManagerLoginController
from entity.idpCategory import IDPCategory


class SearchIDPCategoryController:
    def canSearchIDPCategories(self, managerId):
        return PlatformManagerLoginController().getAuthenticatedManager(managerId) is not None

    # UT45.7 to UT45.9
    def searchIDPCategories(self, keyword):
        # tidy up the keyword first - "  Kitchen " should work the same as "Kitchen"
        # and just spaces counts as empty (shows everything)
        if keyword is None:
            keyword = ""
        keyword = keyword.strip()

        categories = IDPCategory().searchIDPCategories(keyword)
        return categories
