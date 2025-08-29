from .minimization_logic import MinimizationEngine

__version__ = "0.1.0"
__all__ = ["run_minimization"]

def run_minimization(vcon_data, config_path="config.yaml"):
    engine = MinimizationEngine(config_path)
    return engine.run(vcon_data)
