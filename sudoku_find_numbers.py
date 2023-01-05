from google.colab.patches import cv2_imshow
import numpy as np
import cv2
import matplotlib.pyplot as plt
import imutils
from imutils.perspective import four_point_transform

def thresholding(img, debug = False):
  """
  Inputs: colour image, BOOL debug 
  Outputs: thresholded image
  """
  #convert to greyscale
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  #apply gaussian blur to the image
  blurred = cv2.GaussianBlur(img,(5,5),0)
  #apply adaptive gaussian thresholding to blurred image
  thresholded = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2) 
  #invert the image
  thresholded = cv2.bitwise_not(thresholded, thresholded)

  if debug == True:
    cv2_imshow(thresholded)

  return thresholded

def find_main_square(img, alpha = 0.02, debug = False):
  """
  Inputs: thresholded image, alpha to control maximum distance from contour to approximated contour ,BOOL debug 
  Outputs: cropped area of the sudoku puzzle 
  """
  #find contours in thresholded image
  contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  #sort contours from largest area to smallest
  contours = imutils.grab_contours(contours)
  contours = sorted(contours, key = cv2.contourArea, reverse = True)

  #initialise our main square contour
  main_square = None
  #loop over all the contours
  for contour in contours:
    #find permieter of closed contour
    perimeter = cv2.arcLength(contour, True)
    #approximate the closed contour using the Douglas-Peucker algorithm
    #epsilon = alpha*perimeter
    approximation = cv2.approxPolyDP(contour, alpha*perimeter, True)
    #if our approximated contour has four points, we assume it is the outline of the puzzle (square)
    if len(approximation) == 4:
      main_square = approximation
      if debug == True:
        img_show = img
        cv2.drawContours(img_show, [contour], 0, (0,255,0), 3)
        cv2_imshow(img_show)
      break

  return main_square

def crop_and_warp(img,square, debug = False):
  """
  inputs: thresholded image, points corresponding to sudoku square, BOOL debug
  outputs: cropped and warped image of only the sudoku square
  """

  warped_img = four_point_transform(img, square.reshape(4, 2))

  if debug == True:
    cv2_imshow(warped_img)

  return warped_img

def remove_noise(img, min_size):
  # apply connected component analysis to the thresholded image
  num_labels, img_separated, stats, _ = cv2.connectedComponentsWithStats(img)
  sizes = stats[:, -1]
  sizes = sizes[1:]
  num_labels -= 1

  # output image with only the kept components
  img_result = np.zeros((img.shape))
  # for every component in the image, keep it only if it's above min_size
  for label in range(num_labels):
      if sizes[label] >= min_size:
          # see description of im_with_separated_blobs above
          img_result[img_separated == label + 1] = 1

  return img_result

def split_into_digits(img, border_percent = 0.10, rows = 9, columns = 9, debug = False):
  """
  inputs: sudoku puzzle img, border_percent between 0 and 0.5, number of rows and columns puzzle has, BOOL debug
  outputs: individual images of numerical digits in the puzzle by splitting image into an even grid
  """
  #get variables for height and width
  img_height=img.shape[0]
  img_width=img.shape[1]
  #set variables for jumping across image
  x1 = 0
  y1 = 0
  M = img_height//rows
  N = img_width//columns
  #resize image to be divisible by M,N
  img = cv2.resize(img,(N*columns,M*rows))
  digits = []
  #add size of border to be removed to keep only digit in center
  border_size_x = int(border_percent * M)
  border_size_y = int(border_percent * N)
  #loop over rows and columns
  for y in range(0,img_height-M,M):
    for x in range(0, img_width-N, N):
      #get places where to split
      y1 = y + M
      x1 = x + N
      #get tile
      digit = img[y:y+M,x:x+N]
      #remove border
      digit = digit[border_size_y: -1 - border_size_y, border_size_x: -1 - border_size_x]
      digit = remove_noise(digit, 50)
      digits.append(digit)

      if debug == True:
        cv2_imshow(digit)

  return digits

def get_sudoku_digits(img_path):
  #load image
  img = cv2.imread(img_path)
  #threshold image
  thresholded_img = thresholding(img)
  #find contour of sudoku puzzle
  main_square = find_main_square(thresholded_img)
  #get image of just sudoku puzzle
  warped_img = crop_and_warp(thresholded_img, main_square, debug = False)
  #separate into grid 
  digits = split_into_digits(warped_img, debug = False)
  return digits

"""
#Google Collab setup 
from google.colab import drive
drive.mount('/content/drive/')                                                                             
data_dir = '/content/drive/My Drive/self_projects/sudoku/'

#image paths
img1_path = data_dir+'sudoku_pic_1.png'

get_sudoku_digits(img1_path)
"""
