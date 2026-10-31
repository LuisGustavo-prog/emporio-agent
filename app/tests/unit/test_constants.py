from emporio_agent.core import constants


def test_installment_tiers_are_ordered():
    maxes = [t[0] for t in constants.INSTALLMENT_TIERS]
    assert maxes == sorted(maxes)
    assert maxes[-1] == 12
