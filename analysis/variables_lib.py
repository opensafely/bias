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
