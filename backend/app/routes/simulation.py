from ..extension import limiter



@bp.route("/simulation/next", methods=["GET"])
@limiter.limit("30 per minute")
def next_scenario():
    ...