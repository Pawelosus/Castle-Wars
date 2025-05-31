import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torch.optim.lr_scheduler import ReduceLROnPlateau
from models.MoveDataset import MoveDataset
from models.ValueNet import ValueNet
from argparse import ArgumentParser

def train(device='cpu', resume_path=None):
    csv_file = 'move_data.csv'
    batch_size = 1024
    learning_rate = 1e-3
    epochs = 50
    train_split = 0.8

    full_dataset = MoveDataset(csv_file)
    train_size = int(train_split * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    model = ValueNet().to(device)

    if resume_path:
        model.load_state_dict(torch.load(resume_path, map_location=device))
        print(f'Loaded weights from {resume_path}')

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.5,
        patience=3
    )

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0

        for batch in train_loader:
            inputs, labels = batch
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f'Epoch {epoch+1}/{epochs} - Training Loss: {avg_loss:.4f}')

        model.eval()
        val_loss = 0.0
        correct = 0
        with torch.no_grad():
            for batch in val_loader:
                inputs, labels = batch
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                val_loss += criterion(outputs, labels).item()
                correct += ((outputs > 0) == (labels > 0)).sum().item()

        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = correct / len(val_dataset) * 100
        print(f'Validation Loss: {avg_val_loss:.4f}, Direction Match: {val_accuracy:.2f}%')

        scheduler.step(avg_val_loss)
        for i, param_group in enumerate(optimizer.param_groups):
            print(f'Epoch {epoch+1}: LR = {param_group["lr"]}')


    torch.save(model.state_dict(), 'value_net.pth')
    print('Model saved to value_net.pth')

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-model', type=str, default=None, help='path to model .pth file to load')
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    train(device, args.model)
