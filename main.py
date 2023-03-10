def main():
  #Google Collab setup 
  from google.colab import drive
  drive.mount('/content/drive/')                                                                             
  data_dir = '/content/drive/My Drive/self_projects/sudoku/'
  img_paths = ['sudoku_pic_1.png', 'sudoku_pic_2.png']

  #imports 
  import sys
  sys.path.insert(0,data_dir)
  import sudoku_solver
  import sudoku_find_numbers
  import sudoku_identify_digit
  import torch
  import cv2
  from google.colab.patches import cv2_imshow
  import numpy as np

  for img_path in img_paths:
    #get image and isolate numbers
    digits = sudoku_find_numbers.get_sudoku_digits(data_dir + img_path)
    #constants to resize images to fit into CNN (28x28)
    width = 28
    height = 28
    dim = (width, height)

    #load the trained CNN
    #sudoku_net = sudoku_identify_digit.load_network(data_dir, 'sudoku_dl')
    #blank_net = sudoku_identify_digit.load_network(data_dir, 'blank_sudoku_dl')
    path = data_dir + 'sudoku_dl' + '.pt'
    sudoku_net = sudoku_identify_digit.Sudoku_Net(10)
    sudoku_net.load_state_dict(torch.load(path, map_location=torch.device('cpu')))

    #path = data_dir + 'blank_sudoku_dl' + '.pt'
    #blank_net = sudoku_identify_digit.Sudoku_Net(2)
    #blank_net.load_state_dict(torch.load(path, map_location=torch.device('cpu')))

    #create outputs list
    preds = []
    kernel = np.ones((5,5),np.uint8)
    #feed digits into CNN
    for digit in digits:
      # resize image
      digit = cv2.resize(digit, dim, interpolation = cv2.INTER_AREA)
      #cv2_imshow(255*digit)
      #change to a tensor 
      digit_tensor = torch.from_numpy(digit).float()
      #get into right dimensions (1x1x28x28)
      digit_tensor = torch.unsqueeze(torch.unsqueeze(digit_tensor, 0),0)
      #feed into the network
      output = sudoku_net(digit_tensor)
      #turn into prediction
      pred = torch.argmax(output, dim = 1)
      #change to float
      pred = pred.item()
      #add to list
      preds.append(pred)

      #print(pred)
    #print(preds)
    #sort outputs into desired format for our sudoku

    grid = []
    index = 0
    row = []
    for pred in preds:
      row.append(pred)
      index += 1
      if index == 9:
        grid.append(row)
        row = []
        index = 0

    #print(grid)
    #solve the sudoku
    print("Unsolved Grid:")
    sudoku_solver.print_grid(grid)
    sudoku_solver.solve(grid)
    print("Solved Grid:")
    sudoku_solver.print_grid(grid)

 if __name__ == "__main__":
  main()
