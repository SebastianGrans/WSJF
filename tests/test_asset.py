from WSJF.models import SequenceCallStep


def test_add_asset(step: SequenceCallStep):
    """Increases the usage count of asset with serial number "BADDCAFE" by 1.

    This requires there to be an asset with this serial number in the asset manager.

    https://<yourdomain>.wats.com/dist/#/control-panel/asset-manager

    """
    step.add_asset("BADDCAFE", 1)
