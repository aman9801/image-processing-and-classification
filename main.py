import numpy as np
import tkinter as tk
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
from ImageProcessing import ImageProcessing 
import math
from PIL import Image, ImageTk
from os.path import exists


drag_id = ''
placeholder = True
root_w = 0
root_h = 0

# triggered when the window stops being moved 
# (needed to resize the window in case of multiple monitors)
def stop_drag():
    global drag_id
    # expand window to maximized size
    root.state('zoomed')
    # maximum desirable width and height (over this the images would not fit the frame)
    global max_h
    global max_w
    # if image haven't been picked yet
    if placeholder:
        # evaluate max size in "ScreenUnits" 
        max_w = int(root.winfo_width()*.045)
        max_h = int(root.winfo_height()*.025)
        # set size of labels placeholders
        og_img_label.configure(width=max_w, height=max_h)
        og_img_spec_label.configure(width=max_w, height=max_h)
        mod_img_label.configure(width=max_w, height=max_h)
        mod_img_spec_label.configure(width=max_w, height=max_h)
    else:
        # evaluate max size in pixels (needed to resize images)
        max_w = int(root.winfo_width()*.313)
        max_h = int(root.winfo_height()*.373)
        display_images(image, channels)

    # reset drag_id to be able to detect the start of next dragging
    drag_id = ''

def dragging(event):
    global drag_id
    if event.widget is root:  # do nothing if the event is triggered by one of root's children
        if drag_id != '':
            # cancel scheduled call to stop_drag
            root.after_cancel(drag_id)
        # schedule stop_drag
        drag_id = root.after(100, stop_drag)

# fix the image size to fit in the label
def resize_image_to_display(img):    
    # gain current image dimension
    img_w, img_h = img.size
    # calculate current image aspect ratio
    aspect_ratio = img_w/img_h
    # evaluate which dimension to take for max dimension defined above so that the other does 
    # not exceed maximum size limit 
    if max_h*aspect_ratio <= max_w:
        # (max_h*aspect_ratio) = resized width mantaining the aspect ratio, 
        # if that does not exceed the width limit means our image optimal dimension is
        # (max_h*aspect_ratio), max_h) 
        new_size = (int(max_h*aspect_ratio), max_h)
    else:
        # if max_h*aspect_ratio > max_w means that using max_h for our image dimension will cause
        # the width to be too large, as consequence we should take max width and elaborate height 
        # as follows: max_w/aspect_ratio
        new_size = (max_w, int(max_w/aspect_ratio))
    
    res_img = img.resize(new_size)
    return res_img

# show images in the labels
def display_images(image, channels):
    # if working with color 
    if len(channels):
        # convert image from np array to image and resize it
        og_img = resize_image_to_display(Image.fromarray(image.image))
        # convert image to tk photo image
        tk_og_img = ImageTk.PhotoImage(image = og_img)
        # convert image from np array to image and resize it
        sp_og_img = resize_image_to_display(Image.fromarray(image.magnitude_spectrum_RGB[0]))
        # convert image to tk photo image
        tk_sp_og_img = ImageTk.PhotoImage(image = sp_og_img)
        # convert image from np array to image and resize it
        filtered_img = resize_image_to_display(Image.fromarray(image.filtered_image_RGB))
        # convert image to tk photo image
        tk_filtered_img = ImageTk.PhotoImage(image = filtered_img)
        # convert image from np array to image and resize it
        sp_filtered_img = resize_image_to_display(Image.fromarray(image.filtered_magnitude_spectrum_RGB[0]))
        # convert image to tk photo image
        tk_sp_filtered_img = ImageTk.PhotoImage(image = sp_filtered_img)
    else:
        # convert image from np array to image and resize it
        og_img = resize_image_to_display(Image.fromarray(image.image_gray))
        # convert image to tk photo image
        tk_og_img = ImageTk.PhotoImage(image = og_img)
        # convert image from np array to image and resize it
        sp_og_img = resize_image_to_display(Image.fromarray(image.magnitude_spectrum_gray))
        # convert image to tk photo image
        tk_sp_og_img = ImageTk.PhotoImage(image = sp_og_img)
        # convert image from np array to image and resize it
        filtered_img = resize_image_to_display(Image.fromarray(image.filtered_image_gray))
        # convert image to tk photo image
        tk_filtered_img = ImageTk.PhotoImage(image = filtered_img)
        # convert image from np array to image and resize it
        sp_filtered_img = resize_image_to_display(Image.fromarray(image.filtered_magnitude_spectrum_gray))
        # convert image to tk photo image
        tk_sp_filtered_img = ImageTk.PhotoImage(image = sp_filtered_img)

    # display images
    og_img_label.image = tk_og_img
    og_img_label.configure(image = tk_og_img)
    og_img_spec_label.image = tk_sp_og_img
    og_img_spec_label.configure(image = tk_sp_og_img, width=max_w, height=max_h)
    mod_img_label.image = tk_filtered_img
    mod_img_label.configure(image = tk_filtered_img, width=max_w, height=max_h)
    mod_img_spec_label.image = tk_sp_filtered_img
    mod_img_spec_label.configure(image = tk_sp_filtered_img, width=max_w, height=max_h)

#  load the image and create the ImageProcessing object
def load_image(file_path):
    if file_path != '':
        global image
        image = ImageProcessing(file_path)
        
        global max_h, max_w, placeholder
        placeholder = False
        max_w = int(root.winfo_width()*.313)
        max_h = int(root.winfo_height()*.373)

        display_images(image, channels)
        
        label_file_explorer.config(text = f"Selected file: {file_path}")
        label_file_explorer.update()

        button_filter['state'] = 'normal'

# switch the selected color settings and the relative channels
def color_change(*args):
    global channels
    if selected.get() == 'RGB':
        channels = [0,1,2]
    else:
        channels = []
    display_images(image, channels)

# pick the file to transform
def browseFiles():
    global file_path
    file_path = askopenfilename(title = "Select a File", filetypes = [("Images", "*.jpeg"), ("all files", "*.*")])
    load_image(file_path)
    
#  apply the filter with the selected variables
def apply_filter():
    
    if selected.get() == 'RGB':
        channels = [0,1,2]
    else:
        channels = []

    direction = var_filter.get()
    radius = sli_radius.get()
    intensity = sli_intensity.get()
    image.custom_filter(channels, radius, intensity, direction)
    display_images(image, channels)

def main():
    # Create the root window and set it's parameters
    global root
    root = tk.Tk()
    root.title('Image processing')
    root.state('zoomed')
    root.resizable(width=False, height=False)
    root.bind('<Configure>', dragging)
    root.config(background = "white", padx=5, pady=5)

##############################################################################################################################################
    global general_controls_area
    general_controls_area = tk.Frame(root, bg='gray95')
    general_controls_area.config(highlightcolor='black', highlightbackground='black', highlightthickness=1)
    general_controls_area.pack(side='top', fill="x", pady=(10,0))
    # Create button to start the File Explorer
    button_explore = tk.Button(general_controls_area, text = "Select image...", height=2, width=15, command = browseFiles, fg='#000')  
    button_explore.pack(side='left', fill='none', expand=False, padx=25)
    # Create a File Explorer label and set it's parameters
    global label_file_explorer 
    label_file_explorer= tk.Label(general_controls_area, text = f"No file selected", height = 5, fg = "black", bg='gray95')
    label_file_explorer.pack(side='left', fill='x', pady=5, padx=2)
    # Create button for closing the program
    button_exit = tk.Button(general_controls_area, text = "Exit", height=2, width=10, command = exit, fg='#000')
    button_exit.pack(side='right', fill='none', expand=False, padx=25)

##############################################################################################################################################
    # create and position frame containing images and filter controls
    global frame
    frame = tk.Frame(root, bg='gray95')
    frame.config(highlightcolor='black', highlightbackground='black', highlightthickness=1)
    frame.pack(side='bottom', expand=True, fill="both",pady=(0, 10))
    
    ##########################################################################################################################################
    # create and position the area containing the images
    global images_area
    images_area = tk.Frame(frame, bg='gray95')
    images_area.config(highlightcolor='black', highlightbackground='black', highlightthickness=1)
    images_area.pack(side='left', fill='both', expand=True)
    # set up and placement of the label that will contain original image
    global og_img_label
    og_img_label = tk.Label(images_area, bg='gray95', text='Original image will appear here', borderwidth=1, relief='solid', fg='#000')
    og_img_label.place(rely=.02, relx=0.02, relheight=.45, relwidth=.45)
    # set up and place of arrow from original image to it's spectrum 
    arrow1 = tk.Canvas(images_area, bg='gray95',width=50, height=20, border=0)
    arrow1.create_line(0, 10, 50, 10, fill='black', width=5, arrow=tk.LAST)
    arrow1.place(rely=.22, relx=.48)
    # set up and placement of the label that will contain original image magnitude spectrum
    global og_img_spec_label
    og_img_spec_label = tk.Label(images_area, bg='gray95', text='Original image spectrum will appear here', borderwidth=1, relief='solid', fg='#000')
    og_img_spec_label.place(rely=.02, relx=0.53, relheight=.45, relwidth=.45)
    # set up and place of arrow from original spectrum to modified spectrum 
    arrow2 = tk.Canvas(images_area, bg='gray95', width=20, height=50, border=0)
    arrow2.create_line(10, 0, 10, 50, fill='black', width=5, arrow=tk.LAST)
    arrow2.place(relx=.76, rely=.47)
    # set up and placement of the label that will contain modified image magnitude spectrum
    global mod_img_label
    mod_img_label = tk.Label(images_area, bg='gray95', text='Modified image will appear here', borderwidth=1, relief='solid', fg='#000')
    mod_img_label.place(rely=.53, relx=0.02, relheight=.45, relwidth=.45)
    # set up and place of arrow from modified spectrum to modified image 
    arrow3 = tk.Canvas(images_area, bg='gray95', width=50, height=20, border=0)
    arrow3.create_line(50, 10, 0, 10, fill='black', width=5, arrow=tk.LAST)
    arrow3.place(relx=.48, rely=.76)
    # set up and placement of the label that will contain modified image 
    global mod_img_spec_label
    mod_img_spec_label = tk.Label(images_area, bg='gray95', text='Modified image spectrum will appear here', borderwidth=1, relief='solid', fg='#000')
    mod_img_spec_label.place(rely=.53, relx=0.53, relheight=.45, relwidth=.45)
    
    ##########################################################################################################################################
    global controls_area
    controls_area = tk.Frame(frame, bg='gray95')
    controls_area.config(highlightcolor='black', highlightbackground='black', highlightthickness=1)
    controls_area.pack(side='right', fill='y')
    # Dropdown
    # list of color options
    global color_options
    color_options = ['RGB', 'Grayscale']
    # variable containing dropdown selected value
    global selected 
    selected = tk.StringVar()
    selected.set(color_options[0])
    selected.trace('w', color_change)
    # initialize channels
    global channels 
    channels = [0,1,2] 
    # actual dropdown element
    global dropdown
    dropdown = tk.OptionMenu(controls_area, selected, *color_options)
    dropdown.config(width=25, fg='#000')
    dropdown.pack(side='top', fill='x', padx=15, pady=50)
    # Radio buttons
    # variable containing the radio button selection 
    global var_filter
    var_filter = tk.IntVar()
    # actual radio button element
    R1 = tk.Radiobutton(controls_area, text="HPF", variable=var_filter, value=0, fg='#000')
    R1.pack(side='top', fill='x', padx=15, pady=(20,10))
    R2 = tk.Radiobutton(controls_area, text="LPF", variable=var_filter, value=1, fg='#000')
    R2.pack(side='top', fill='x', padx=15, pady=(10,20))
    # Slider radius
    global sli_radius, sli_intensity
    sli_radius = tk.Scale(controls_area, from_=0, to=100, orient=tk.HORIZONTAL, label='Radius of filter (% of image width)', tickinterval=10, fg='#000')
    sli_radius.pack(side='top', fill='x', padx=15, pady=20)
    # Slider intensity
    label_text = f"Dampening intensity (% of image width)"
    sli_intensity = tk.Scale(controls_area, from_=0, to=99.9, orient=tk.HORIZONTAL, label=label_text, tickinterval=10, fg='#000')
    sli_intensity.pack(side='top', fill='x', padx=15, pady=20)
    # Button to apply filter
    global button_filter
    button_filter = tk.Button(controls_area, text = "Filter", height=2, width=15, command = apply_filter, fg='#000')  
    button_filter['state'] = 'disabled'
    button_filter.pack(side='bottom', fill='x', padx=15, pady=(30,10))



    # Let the window wait for any events
    root.mainloop()

# check if the process running is the 'main', in that case start 
if __name__ == '__main__':
    main()