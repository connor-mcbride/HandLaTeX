import torch
import torch.nn as nn

class StrokeLSTMClassifier(nn.Module):
    def __init__(self, input_size=3, hidden_size=128, num_layers=2, num_classes=10, dropout=0.3, bidirectional=True):
        """
        Args:
            input_size (int): Number of input features per time step (e.g., 2 for x and y).
            hidden_size (int): Number of features in the hidden state.
            num_layers (int): Number of recurrent layers.
            num_classes (int): Number of output classes.
            dropout (float): Dropout probability.
            bidirectional (bool): If True, becomes a bidirectional LSTM.
        """
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional

        # LSTM layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=dropout, bidirectional=bidirectional)

        # Dropout layer
        self.dropout = nn.Dropout(dropout)

        # Fully Connected Layer
        self.fc = nn.Linear(hidden_size * 2 if bidirectional else hidden_size, num_classes)

    def forward(self, x):
        """
        Args:
            x (torch.Tensor): Padded input tensor of shape (batch_size, seq_length, input_size)

        Returns:
            out (torch.Tensor): Output logits of shape (batch_size, num_classes)
        """
        h0 = torch.zeros(self.num_layers * (2 if self.bidirectional else 1),
                         x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers * (2 if self.bidirectional else 1),
                         x.size(0), self.hidden_size).to(x.device)

        # Forward propagate through LSTM
        out, _ = self.lstm(x, (h0, c0))

        # Take the output from the last time step
        out = out[:, -1, :]

        out = self.dropout(out)
        out = self.fc(out)
        return out
