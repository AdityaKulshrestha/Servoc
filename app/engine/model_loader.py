import torch


# Load your model here

class Model:
    def __init__(self):
        # Dummy model for illustration; replace with actual model loading
        self.model = torch.nn.Linear(10, 2)  # Example model

    def predict(self, input_data: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            return self.model(input_data)