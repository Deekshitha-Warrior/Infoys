"""Public Python API for CareerCast 0.4.0. No database writes on import."""
__version__ = "0.4.0"


def predict_profile(profile, k=5):
    from app.schemas import ProfileBase
    from app.intelligence import predict
    return predict(ProfileBase.model_validate(profile).model_dump(), k)


def skill_gap(profile, career):
    from app.schemas import ProfileBase
    from app.gaps import gap_report
    return gap_report(ProfileBase.model_validate(profile).model_dump(), career)
