import asyncio

from source.framework.meeseeks_multi_turn_framework import MeeseeksMultiTurnFramework
from source.model.demo_api_model import DemoApiModel

if __name__ == "__main__":
    # Data to be evaluated
    data_path = "Meeseeks_quickstart_data.json"
    # Target Model. Implement your own model class and create an instance here. See README quickstart.
    target_model = DemoApiModel(ip="1")
    # Extraction Model. Implement your own model class and create an instance here. See README quickstart.
    extract_model = DemoApiModel(ip="")
    # Scoring Model. Implement your own model class and create an instance here.  See README quickstart.
    score_model = DemoApiModel(ip="")


    # Run the evaluation
    framework = MeeseeksMultiTurnFramework(target_model=target_model,
                               extract_model=extract_model,
                               score_model=score_model,
                               data_path=data_path,
                               total_rounds=3,
                               concurrency=50) # Rounds can be set here, default to 3.
    asyncio.run(framework.run())