import glob
import time 
import random
import numpy as np
from torchvision import datasets
from torchvision import transforms
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import torch
import torchvision
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.mobile_optimizer import optimize_for_mobile
from google.colab.patches import cv2_imshow
import cv2

class DigitsDataset(torch.utils.data.Dataset):
  def __init__(self, data_dir, len, blank):
    self.fonts = glob.glob(data_dir +"fonts/*.ttf")
    self.len = len
    self.data = [None] * self.__len__()
    self.blank = blank
    self.generate_all()

  def __len__(self):
    return self.len

  def __getitem__(self, index):
    return self.data[index]

  def generate_all(self):
    for p in range(self.__len__()):
      self.data[p] = self.generate_digit()

  def generate_digit(self):
    digit = random.randint(0, 9)
    picture = self.generate_digit_pil(digit)
    if self.blank == False:
      return picture, torch.tensor(digit)
    else:
      if digit == 0:
        return picture, torch.tensor(0)
      else:
        return picture, torch.tensor(1)

  def generate_digit_pil(self, digit: int):
    font_choice = random.randint(0, len(self.fonts)-1)
    size = random.randint(20,28)
    if digit != 0:
      text = str(digit)
      img = Image.new("L", (28, 28), (0,))
      draw = ImageDraw.Draw(img)
      fnt = ImageFont.truetype(self.fonts[font_choice], size)
      text_x = 28//4 + random.randint(-2, 2)
      text_y = (28//4)-4 + random.randint(-2, 2)
      draw.text((text_x, text_y), text, (255,), font=fnt, anchor="mm")
      img_array = np.array(img)
      noise = (np.random.rand(28,28) < 0.005).astype(float)
      img_array = ((img_array + noise).astype(bool)).astype(float)
    else:
      img_array = ((np.random.rand(28,28) < 0.005).astype(bool)).astype(float)

    img_tensor = torch.from_numpy(img_array)
    img_tensor = img_tensor.unsqueeze(0).float()
    return img_tensor

#set up CNN
class Sudoku_Net(nn.Module):
    def __init__(self, outfeatures):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels = 1, out_channels = 10, kernel_size = 5) 
        self.pool = nn.MaxPool2d(kernel_size = 2, stride = 2) 
        self.conv2 = nn.Conv2d(in_channels = 10, out_channels = 20, kernel_size = 3) 
        self.fc1 = nn.Linear(in_features = 20 * 5 * 5, out_features = 120)
        self.fc2 = nn.Linear(in_features = 120, out_features = 84)
        self.fc3 = nn.Linear(in_features = 84, out_features = outfeatures) 

    def forward(self, x):
        #initial image size 1x28x28
        x = self.pool(F.relu(self.conv1(x))) #convolution - 10x24x24, pool - 10x12x12
        x = self.pool(F.relu(self.conv2(x))) #convolution - 20x10x10, pool - 20x5x5
        x = torch.flatten(x, start_dim = 1) # flatten all dimensions except batch to one 16x6x6 layer
        x = F.relu(self.fc1(x)) #120 node layer
        x = F.relu(self.fc2(x)) #84 node layer
        x = self.fc3(x) #10 node layer - corresponding to digits 1-9 and blank image
        return F.log_softmax(x) #return log softmax to use negative log likelihood loss

def training_process(batch_size, epochs, device, net, train_data):
  #training process

  #use dataloader to help perform training process
  train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=2)

  #set the loss function and optimiser
  #use negative log likelihood loss and stochastic gradient descent
  criterion = nn.NLLLoss()
  optimiser = optim.SGD(net.parameters(), lr = 0.003, momentum = 0.9)

  #create list for losses 
  epoch_loss_list = []
  for epoch in range(epochs):  # loop over the dataset multiple times
      epoch_loss = 0
      for batch_idx, (inputs, labels) in enumerate(train_loader):
          # get the inputs; data is a list of [inputs, labels] and move them to the current device
          inputs = inputs.to(device)
          labels = labels.to(device)

          #zero parameter gradients
          optimiser.zero_grad()
          #send inputs through network
          outputs = net(inputs)
          #find loss 
          loss = criterion(outputs, labels)
          #perform backpropagation
          loss.backward()
          #update network
          optimiser.step()

          #get loss statistics
          epoch_loss += loss.item()
      epoch_loss = epoch_loss/len(train_data.data)
      print(f"epoch:{epoch +1}. Loss: {epoch_loss}")
      epoch_loss_list.append(epoch_loss)

      #if loss is only being reduced by small amount, stop training as to avoid overtraining
      if epoch > 1 and epoch_loss_list[-2] - epoch_loss_list[-1] < 0.0005:
          break

  #plot loss
  x_axis_scatter = [i for i in range(len(epoch_loss_list))]
  plt.scatter(x_axis_scatter, epoch_loss_list)

  return net

#use dataloader process
#batch_size = 4
#train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=2)
#test_loader = torch.utils.data.DataLoader(test_data, batch_size=batch_size, shuffle=True, num_workers=2)

def test_network(net, device, test_data, batch_size):
  #test network
  #find average correct percentage 
  test_loader = torch.utils.data.DataLoader(test_data, batch_size=batch_size, shuffle=True, num_workers=2)
  # prepare to count predictions for each class using dictionary (0 = blank)
  correct_counter = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0}
  total_counter = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0}

  with torch.no_grad():
    #loop through the test data
    for batch_idx, (inputs, labels) in enumerate(test_loader):
      inputs = inputs.to(device)
      labels = labels.to(device)
      outputs = net(inputs)
      #get prediction from network
      preds = torch.argmax(outputs, dim = 1)
      labels = labels.to("cpu")
      preds = preds.to("cpu")
      labels = labels.numpy()
      preds = preds.numpy()
      preds = torch.argmax(outputs, dim = 1)
      # collect the correct predictions for each class
      for index in range(batch_size):
        total_counter[labels[index]] += 1
        if preds[index] == labels[index]:
          correct_counter[labels[index]] += 1
  # print accuracy for each class
  for index in range(10):
    accuracy = 100* float(correct_counter[index])/total_counter[index]
    print(f"Class {index} Accuracy: {accuracy}%")

def save_network(net, data_dir, name):
  #save the network 
  path = data_dir + name + '.pt'
  torch.save(net.state_dict(), path)

def load_network(data_dir, name):
  #load network
  path = data_dir + name + '.pt'
  net = Sudoku_Net()
  net.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
  return net

def save_model_mobile(net, data_dir):
  #save model to be able to work for mobile app
  example = torch.rand(1,1,28,28)
  net = net.to("cpu")

  #trace and optimise
  traced_module = torch.jit.trace(net, example)
  optimised_model = optimize_for_mobile(traced_module)

  path = data_dir + 'sudoku_dl_mobile_opt.pt'
  optimised_model.save(path)

"""#Google Collab setup 
from google.colab import drive
drive.mount('/content/drive/')                                                                             
data_dir = '/content/drive/My Drive/self_projects/sudoku/'

#create and load dataset
train_data = DigitsDataset(data_dir, 50000, True)
test_data = DigitsDataset(data_dir, 10000, True)

#setup using GPU is it is available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"The current device is {device}")
blank_net = Sudoku_Net(2).to(device)

#choose batch size and epoches
batch_size = 4
epochs = 100

#train network
net = training_process(batch_size, epochs, device, blank_net, train_data)

#test network
#test_network(net = net, device = device, test_data = test_data, batch_size = batch_size)

#save network
save_network(net, data_dir, 'blank_sudoku_dl')

#Google Collab setup 
from google.colab import drive
drive.mount('/content/drive/')                                                                             
data_dir = '/content/drive/My Drive/self_projects/sudoku/'

#create and load dataset
train_data = DigitsDataset(data_dir, 50000)
test_data = DigitsDataset(data_dir, 10000)

#setup using GPU is it is available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"The current device is {device}")
net = Sudoku_Net(10).to(device)

#choose batch size and epoches
batch_size = 4
epochs = 100

#train network
net = training_process(batch_size, epochs, device, net, train_data)

#test network
test_network(net = net, device = device, test_data = test_data, batch_size = batch_size)

#save network
save_network(net, data_dir)

#Google Collab setup 
from google.colab import drive
drive.mount('/content/drive/')                                                                             
data_dir = '/content/drive/My Drive/self_projects/sudoku/'

#get dataset
train_data, test_data = get_mnist(data_dir)
train_data, test_data = data_preprocessing(data_dir)
get_stats(train_data, test_data)

#setup using GPU is it is available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"The current device is {device}")
net = Sudoku_Net().to(device)

#choose batch size and epoches
batch_size = 4
epochs = 100

#train network
net = training_process(batch_size, epochs, device, net, train_data)

#save network
save_network(net, data_dir)

#if already saved
load_network(data_dir)

#test network
test_network(test_loader, net, device, test_data)

#get MNIST dataset
def get_mnist(data_dir):
  train_data = datasets.MNIST(
      root = data_dir,
      train = True,                         
      transform = ToTensor(), 
      download = True,            
  )
  test_data = datasets.MNIST(
      root = data_dir, 
      train = False, 
      transform = ToTensor()
  )
  return train_data, test_data

#get info on dataset
def get_stats(train_data, test_data):
  print(train_data)
  print(test_data)

  print(f"train data size: {train_data.data.size()}")
  print(f"train data targets size: {train_data.targets.size()}")
  #visualise dataset
  plt.imshow(test_data.data[0], cmap='gray')
  plt.title('%i' % test_data.targets[0])
  plt.show()
  #find max and min values 
  print(torch.max(train_data.data))
  print(torch.min(train_data.data))

#Data Preprocessing

def data_preprocessing(train_data, test_data):
  #Remove the examples that are 0, as this will not be used in sudoku, and replace with a blank image with some noise
  for index in range(int(train_data.targets.size(0))):
    if train_data.targets[index] == 0:
      blank_image = (torch.rand(size=(train_data.data.size(1), train_data.data.size(2))) < 0.05).float()
      train_data.data[index,:,:] = blank_image

  #do same for test data
  for index in range(int(test_data.targets.size(0))):
    if test_data.targets[index] == 0:
      blank_image = 255*(torch.rand(size=(test_data.data.size(1), test_data.data.size(2))) < 0.05).float()
      test_data.data[index,:,:] = blank_image

  return train_data, test_data
"""
