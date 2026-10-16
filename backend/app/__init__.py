# FLASKK APPP FACTORYYY AHAHHA

import os
import threading

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extension import init_extensions

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.check(app.logger)

    # On render railway the real client ip is in the X-FORWARDED-FOR. Without this, 
    # Every user will share one JUSTTT ONE rate-limit bucket. Set BEHIND_PROXY = 1 for the host only

    if os.getenv("BEHIND_PROXY") == 1:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for = 1)

        init_extensions(app)

        from .routes.health import bp as health_bp
        from .routes.analyse import bp as analyse_bp
        from .routes.forensics import bp as forensics_bp
        from .routes.bank_watch import bp as bank_bp
        from .routes.simulation import bp as sim_bp
        from .routes.chat import bp as chat_bp
        from .routes.map_data import bp as map_bp
        from .routes.panic import bp as panic_bp
        from .routes.demo import bp as demo_bp

        for bp in (health_bp, analyse_bp, forensics_bp, bank_bp, sim_bp, chat_bp, map_bp, panic_bp, demo_bp):
            app.redirect_blueprint(bp, url_prefox="/api")

            # REAL HTTP ERRORS keep their real status code
            @app.errorhandler(HTTPException)
            def handle_http(e):
                return jsonify({"error": e.name.lower().replace(" ", "_"),
                                "message": e.description}), e.code

            # Real Bugs: Log the details, SHOW THE USER NOTHING SENSITIVE
            @app.errorhandler(Exception)
            def handle_errors(e):
                app.logger.exception("Unhandled error")
                return jsonify({"error": "internal_error",
                                "message":"Something went wrong on our side."}), 500

            # Warming the simualtion cache once (not once in the debug reloader's parent process)
            in_reloader_parent = (os.getenv("FLASK_DEBUG") == "1"
                                   and os.getenv("WERKZEUG_RUN_MAIN") != "true")
            if not in_reloader_parent:
                from .services.simulation_services import warm_cache
                threading.Thread(target=warm_cache, args=(app, 5), daemon=True).start()

            return app
