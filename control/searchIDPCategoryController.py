# Control: SearchIDPCategoryController - UC45 Search IDP categories (US45)

from entity.idpCategory import IDPCategory


class SearchIDPCategoryController:
    # UC45 Search IDP categories
    # the page tidies up the keyword - this just calls search (empty keyword = every category)
    def searchIDPCategories(self, keyword):
        return IDPCategory().searchIDPCategories(keyword)
