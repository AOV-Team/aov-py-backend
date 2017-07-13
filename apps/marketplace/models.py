from apps.account import models as account_models


class MarketplaceUser(account_models.User):
    class Meta:
        proxy = True
        verbose_name_plural = "Marketplace Users"