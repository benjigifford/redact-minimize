from .redaction_logic import RedactionEngine

def run_redaction(vcon_data, config_path="config.yaml"):
    engine = RedactionEngine(config_path)
    return engine.run(vcon_data)
