# importing the module
import cv2
  
from tkinter import *
# function to display the coordinates of
# of the points clicked on the image
def click_event(event, x, y, flags, params):
 
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
 
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)

    # checking for right mouse clicks    
    if event==cv2.EVENT_RBUTTONDOWN:
     
        top = Tk()  
  
        top.geometry("200x100")  
  
        b1 = Button(top,text = "cucina")  
        b2 = Button(top,text = "camera da letto") 
        b3 = Button(top,text = "bagno") 
        b4 = Button(top,text = "sala") 
        b1.pack(side=LEFT)  
        b2.pack(side = RIGHT)  
        b3.pack(side=TOP)  
        b4.pack(side=BOTTOM)  
        top.mainloop()  
      

 
# driver function
if __name__=="__main__":
 
    # reading the image
 
    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.setMouseCallback( click_event)
 
    # wait for a key to be pressed to exit
    cv2.waitKey(0)
 
    # close the window
    cv2.destroyAllWindows()