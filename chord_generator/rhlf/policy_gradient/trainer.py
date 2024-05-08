import argparse
import os
import warnings

import numpy as np
import torch
from src.data import get_data
from src.model import load_model
from src.reward_model import load_reward_model
from src.utils import CustomLogger
from torch.utils.tensorboard import SummaryWriter
from torchmetrics.classification import MulticlassAccuracy

#from tqdm.notebook import tqdm_notebook as tqdm
from tqdm import tqdm

warnings.filterwarnings('ignore')

seed = 1234
np.random.seed(seed)
torch.manual_seed(seed)
# Set the seed for random number generation in PyTorch for all GPU operations for reproducibility
torch.cuda.manual_seed(seed)

# Ensure that the Convolutional Neural Network (CNN) operations are deterministic in PyTorch
# This can help with reproducibility, but may impact performance and can't be used with all models
torch.backends.cudnn.deterministic = True

# Creating necessary Folders if not present.
if not os.path.exists('models/'):
    os.mkdir('models')
if not os.path.exists('logs/'):
    os.mkdir('logs')


if torch.backends.mps.is_available():
    DEVICE = torch.device(device='mps')
elif torch.cuda.is_available():
    DEVICE = torch.device(device='cuda')
else:
    DEVICE = torch.device(device='cpu')


class Single_Core_Trainer:
    def __init__(self: 'Single_Core_Trainer'):
        self.loss_criteria = torch.nn.CrossEntropyLoss()
    
    def _one_epoch_train(self: 'Single_Core_Trainer', model: torch.nn.Module, data_loader_train: torch.utils.data.DataLoader, 
                         optim_alog: torch.optim) -> tuple:
        """Function that trains the model for one epoch.

        Args:
            model (torch.nn.Module): Pytorch model we want to train.
            data_loader_train (torch.utils.data.DataLoader): Pytorch dataloader that carries training data.
            optim_alog (torch.optim): Opimiztion algoritham that we use to update model weights.

        Returns:
            tuple: Output tensor carrying predicted probability of each class.
        """
        batch_loss_train = []
        batch_accuracy_train = []
        batch_counter = 0
        for batch in tqdm(data_loader_train):
            inputs = batch["ids"].to(device=DEVICE)
            attention_mask = batch['attention_masks'].to(device=DEVICE)
            start_label = batch['start_label'].to(device=DEVICE)
            label_vector = batch['label_vector'].to(device=DEVICE)
            
            # Enabling model training.
            model.train(True)
            
            #Setting gradients to zero to prevent gradient accumulation.
            optim_alog.zero_grad()
            
            # Forward pass.
            output, genre, action_log_proba = model(inputs, attention_mask, start_label, label_vector)
            
            chord_vector = start_label + 1.25*output[:,0,:] + 1.5*output[:,1,:] + 1.75*output[:,2,:]
            
            with torch.no_grad():
                chord_vector = chord_vector.to(DEVICE)
                reward = reward_model(inputs, chord_vector, attention_mask)
            
            total_loss = - torch.mean(reward * action_log_proba)
            
            # Back Propagation
            total_loss.backward()
            
            # Updating weights
            optim_alog.step()
            
            batch_counter += 1
            
            del(inputs)
            del(attention_mask)
            del(start_label)
            del(label_vector)
            
        return sum(batch_loss_train)/batch_counter, reward
    
    def training_loop(self: 'Single_Core_Trainer', model: torch.nn.Module, data_loader_train: torch.utils.data.DataLoader, data_loader_test: torch.utils.data.DataLoader, 
                  epochs:int, optim_alog: torch.optim, learning_rate_scheduler:torch.optim =None)-> dict:
        """Function that trains the model for the given number of epochs

        Args:
            model (torch.nn.Module): Pytorch model we want to train.
            data_loader_train (torch.utils.data.DataLoader): Pytorch dataloader that carries training data.
            data_loader_test (torch.utils.data.DataLoader): Pytorch dataloader that carries testing data.
            epochs (int): Count of EPOCHS
            optim_alog (torch.optim): Opimiztion algoritham that we use to update model weights.
            learning_rate_scheduler (torch.optim, optional): Learning rate scheduler to decrease the learning rate. Defaults to None.

        Returns:
            dict: A dictionary that carries the output metrics.
        """
        
        loss_train = []
        loss_test = []
        
        accuracy_train = []
        accuracy_test = []
        
        # Loop that iterates over each EPOCH
        for epoch in tqdm(range(epochs)):
            
            #Train the model for one EPOCH
            epoch_loss, epoch_accuracy = self._one_epoch_train(model, data_loader_train, optim_alog)
            
            loss_train.append(epoch_loss)
            accuracy_train.append(epoch_accuracy)
            
            loss = 0
            accuracy = 0
            loss_test.append(0)
            accuracy_test.append(0)
            
            writer.add_scalar("loss/loss_per_episode", epoch_loss, epoch+pre_trained_epochs)
            writer.add_scalar("reward/reward_per_episode", sum(epoch_accuracy)/64, epoch+pre_trained_epochs)
            
            logger.log_training_info(pretrained_num_epochs+epoch, epoch_loss, epoch_accuracy, loss, accuracy)
            
            
                
            if  not os.path.exists(checkpoint_save_dir):
                os.makedirs(checkpoint_save_dir)
                                                                                                                
            if (epoch+1+pre_trained_epochs)%5 == 0:
                torch.save(model.decoder.state_dict(), os.path.join(checkpoint_save_dir,'epoch_'+str(epoch+1+pre_trained_epochs)+'.pth'))


    
    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Python Single GPU Training Script')

    parser.add_argument('--batch_size', required=False,
                        default=128,
                        metavar="<batchsize to train>",
                        help='Batchsize to Train',
                        type=int)

    parser.add_argument('--learning_rate', required=False,
                        default=3e-4,
                        metavar="<float>",
                        help='Learning Rate',
                        type=float)

    parser.add_argument('--mixed_precision_training', required=False,
                        default=False,
                        metavar="<True/False>",
                        help='Want Mixes Precision Training',
                        type=bool)

    parser.add_argument('--epochs', required=True,
                        metavar="<integer>",
                        help='Number of Epoches',
                        type=int)

    parser.add_argument('--checkpoint_epoches', required=False,
                        default=0,
                        metavar="<integer>",
                        help='What is the checkpoint epoch?',
                        type=int)

    parser.add_argument('--checkpoint_load_path', required=False,
                        default=None,
                        metavar="/path/to/model.pt/",
                        help='Path to model.pt file')


    args = parser.parse_args()
    
    batch_size = args.batch_size
    
    learning_rate = args.learning_rate
    mixed_precision_training = args.mixed_precision_training
    
    epochs = args.epochs
    pre_trained_epochs = args.checkpoint_epoches
    checkpoint_load_path = args.checkpoint_load_path
    #Tensorboard_Writer
    
    writer = SummaryWriter(log_dir='tensorboard_logs/'+'lr_'+str(learning_rate).replace('.','p')+'_mpt_'+str(mixed_precision_training))
    
    log_file = 'lr_'+str(learning_rate).replace('.','p')+'_mpt_'+str(mixed_precision_training)+'.log'
    logger = CustomLogger(os.path.join('logs', log_file))
    
    checkpoint_save_dir = os.path.join('models', 'lr_'+str(learning_rate).replace('.','p')+'_mpt_'+str(mixed_precision_training))
    train_data_loader = get_data(batch_size=batch_size)
    
    model = load_model()
    reward_model = load_reward_model()
    # Load Model
    if checkpoint_load_path:
        model.load_state_dict(torch.load(checkpoint_load_path))
        logger.log_model_loading(checkpoint_load_path.split('/')[1], "Model loaded successfully.")
    else:
        pretrained_num_epochs = 0
    
    model = model.to(DEVICE)
    reward_model = reward_model.to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=0.0005)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
    
    # Load Modules incase of Mixed Precision Training.
    trainer = Single_Core_Trainer()
    
    
    trainer.training_loop(model, data_loader_train=train_data_loader, data_loader_test=None, epochs=epochs, 
                          optim_alog=optimizer, learning_rate_scheduler=None)
    batch_loss_test = []
    batch_accuracy_test = []
    batch_counter = 0

    
    writer.flush()
    writer.close()