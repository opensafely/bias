from databuilder.ehrql import case, when
from databuilder.tables.beta import tpp


def practice_registrations_active_for_patient_at(date):
    """
    Return each patient's "active" practice registration as of the supplied date
    """
    regs = tpp.practice_registrations
    overlapping = regs.take(
        regs.start_date.is_on_or_before(date)
        & (regs.end_date.is_after(date) | regs.end_date.is_null())
    )
    # If there are multiple registrations overlapping we use the one with the most
    # recent start date. If there are multiple of these we use the longest. As a
    # tie-breaker we use the practice psuedo ID.
    return overlapping.sort_by(
        overlapping.start_date,
        overlapping.end_date,
        overlapping.practice_pseudo_id,
    ).last_for_patient()


def addresses_active_for_patient_at(date):
    """
    Return each patient's "active" address as of the supplied date
    """
    addr = tpp.addresses
    overlapping = addr.take(
        addr.start_date.is_on_or_before(date)
        & (addr.end_date.is_after(date) | addr.end_date.is_null())
    )
    # Where there are multiple overlapping address registrations we need to pick one.
    # Logic copied from:
    # https://github.com/opensafely-core/cohort-extractor/blob/e77a0aa2/cohortextractor/tpp_backend.py#L1756-L1773
    ordered = overlapping.sort_by(
        # Prefer the most recently registered address
        addr.start_date,
        # Prefer the address registered for longest
        addr.end_date,
        # Prefer addresses with a postcode
        case(when(addr.has_postcode).then(1), default=0),
        # Use the opaque ID as a tie-breaker for sort stability (we invert this simply
        # so the order matches the original order defined in Cohort Extractor to
        # facilitate direct comparison)
        -addr.address_id,
    )
    return ordered.last_for_patient()
