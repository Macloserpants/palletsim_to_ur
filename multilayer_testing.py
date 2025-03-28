import tkinter as tk
from tkinter import ttk

import numpy as np
import json
import socket
import threading
import queue
import psutil

import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from box import Box

PORT = 50000
# Row / Col editing

# Row
IP_ADDRESS_1 = 0
IP_ADDRESS_2 = 1
PALLET_WIDTH = 2
PALLET_HEIGHT = 3
PALLET_UPDATE = 4

BOX_WIDTH = 5
BOX_HEIGHT = 6
ADD_DELETE_BOX_ROW = 7
ROTATE_BOX = 8

JOG_DISTANCE = 9
JOG_UP_RIGHT_ROW = 10
JOG_DOWN_LEFT_ROW = 11

ADD_DELETE_LAYER = 12
NEXT_PREVIOUS_LAYER = 13

GRID_LAYOUT = 14

# Column
COLUMN_0 = 0
COLUMN_1 = 1
COLUMN_2 = 2
COLUMN_3 = 3

dragging_box = None
offset_x = 0
offset_y = 0
selected_box = None
current_layer = 0

layers = [[]]
list_of_pose = [[]]

stop_event = threading.Event()
connection_established = False
client_connection = None

# main window
root = tk.Tk()
root.title("Pallet and Boxes")

def on_closing(stop_event):
    """Handle the window closing event to stop the server thread."""
    # global stop_event
    if stop_event:
        stop_event.set()  # Signal the server thread to stop
    root.quit()  # Exit the mainloop

def polling_mainloop():
    update_canvas()
    update_gui_from_server()  # Update the GUI based on messages from the server
    root.after(100, polling_mainloop)  # Keep checking the message queue every 100ms

def get_ethernet_ip():
    for interface, addrs in psutil.net_if_addrs().items():
        print(f"Interface: {interface}")  # Debugging line to show which interface is being processed

        # Check if it's an Ethernet interface (Adjust this name depending on your system)
        # if "Ethernet " in interface:
        if "lan3" in interface:
            for addr in addrs:
                # Look for an IPv4 address
                if addr.family == socket.AF_INET:
                    print(f"Found IP: {addr.address}")  # Debugging line to show found IP
                    print(f"PORT: {PORT}")
                    return addr.address
                else:
                    no_ethernet_connection = "Check your ethernet connection"  
    return no_ethernet_connection  # If no Ethernet interface is found

def server_thread_func(stop_event):
    global connection_established, client_connection

    IP_ADDRESS = get_ethernet_ip()
    
    while not stop_event.is_set():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((IP_ADDRESS, PORT)) 
                sock.listen()
                print(type(IP_ADDRESS))
                print (f"Server listening on {IP_ADDRESS}:{PORT}")    
                server_label.config(text="Server Status: Waiting for Socket Connection")


                conn, addr = sock.accept()
                client_connection = conn
                connection_established = True

                with client_connection:
                    print(f"Connected by {addr}")
                    server_label.config(text="Server Status: Connected")
                    while True:
                        update_gui_from_server
                        data = client_connection.recv(1024)
                        if not data:
                            break
                        print(f"Received: {data.decode()}")
                        client_connection.sendall(b"Hello from server!")
                        message_queue.put(f"Received from client: {data.decode()}")  # Put message into the queue for GUI
                        
            except Exception as e:
                update_server_status("(Error) Read terminal for details")
                print(f"Error: {str(e)}")
            finally:
                sock.close()

def set_server_connection():
    
    """Start the server in a separate thread."""
    server_thread = threading.Thread(target=server_thread_func, args=(stop_event,))
    server_thread.daemon = True  # This ensures the thread exits when the main program exits
    server_thread.start()

def _update_server_status_label(message):
        server_label.config(text=f"Server Status: {message}")

def update_server_status(message):
        # Update the label text from the socket communication thread
        # This method must run in the main GUI thread
        root.after(0, _update_server_status_label, message)

def update_gui_from_server():
    try:
        # Check if there's a new message from the server thread
        message = message_queue.get_nowait()
        message_out_label.config(text=message)
    except queue.Empty:
        pass
    
    # Keep checking for messages while the GUI is running
    root.after(100, update_gui_from_server)


def send_to_robot():
    global connection_established, client_connection

    if connection_established and client_connection:
        try:
        
            # Whats the best way to transfer the data?
            
            ###### IDEA 1 CSV ##########

            # for box in layers[current_layer]:
            #     center_x = box.x + box.width / 2
            #     center_y = box.y + box.height / 2
            #     csv_data = "\n".join([f"{box.id},{center_x},{center_y},{box.width},{box.height},{box.angle},{box.layer}"])
            # csv_data = "\n".join([f"{box.id},{box.x},{box.y},{box.width},{box.height},{box.angle},{box.layer}" for box in layers[current_layer]])
            # print("CSV DATA:")
            # print(csv_data)
            # client_connection.sendall(csv_data.encode('utf-8'))

            ###### IDEA 2 JSON ##########

            # client_connection.sendall(data.encode('ascii'))  # Send data to client

            # boxes_dict = [box.to_dict() for box in enumerate(layers[current_layer])]
            # # Convert the list of dictionaries to a JSON string
            # json_data = json.dumps(boxes_dict)

            # client_connection.sendall(json_data.encode('urf-8'))  # Send data to client
            
            ###### IDEA 3 ASCII ##########

            # bytes_sent = client_connection.sendall(data.encode('ascii'))
            # if bytes_sent == len(data.encode('ascii')):
            #     print("Data sent successfully!")
            # else:
            #     print(f"Warning: Only {bytes_sent} bytes were sent out of {len(script)}.")

            ###### IDEA 4 Parse it here and send over a list data in string 1-by-1.
            # 1. Send a Boolean to the robot for monitoring
            # 2. Send a 

            data_list = [[box.id, round(box.x, 2), round(box.y, 2), box.width, box.height, box.angle, box.layer, round(box.x + box.width / 2, 2), round(box.y + box.height / 2, 2)]
            for box in layers[current_layer]]
            print("DATA LIST")
            print(data_list)
            # Convert list to string format that URScript can parse
            data_string = str(data_list).replace("[", "{").replace("]", "}")
            
            print("DATA SENT TO UR:")
            print(data_string)

            client_connection.sendall(data_string.encode('utf-8'))
            
            # print(f"Sent: {csv_data}")
        except Exception as e:
            print(f"Error sending data: {str(e)}")
            update_server_status("Server Status: (Error) Failed to send data")

# KHAIRUL try URScript to robot
def urscript_to_robot():
    pose = [0.138, -0.492, -0.072, 3.14, 0, 0]  # X, Y, Z, RX, RY, RZ in meters and radians
    script = f"""
    def move_robot():
        target_pose = p{pose}  # Use 'p' for pose
        movel(target_pose, a=1.0, v=0.5)
    end
    """
    return script

def get_rotated_bounds(x, y, width, height, angle):
    angle_rad = np.radians(angle)
    cx, cy = x + width / 2, y + height / 2
    corners = np.array([
        [x, y],
        [x + width, y],
        [x + width, y + height],
        [x, y + height]
    ]) - [cx, cy]
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])
    rotated_corners = (corners @ rotation_matrix.T) + [cx, cy]
    return rotated_corners


def boxes_overlap(box1, box2):
    # corners1 = get_rotated_bounds(*box1)
    # corners2 = get_rotated_bounds(*box2)
    corners1 = get_rotated_bounds(box1.x, box1.y, box1.width, box1.height, box1.angle)
    corners2 = get_rotated_bounds(box2.x, box2.y, box2.width, box2.height, box2.angle)

    def min_max(corners):
        return (np.min(corners[:, 0]), np.max(corners[:, 0]), np.min(corners[:, 1]), np.max(corners[:, 1]))

    def is_overlap(corners1, corners2):
        min_x1, max_x1, min_y1, max_y1 = min_max(corners1)
        min_x2, max_x2, min_y2, max_y2 = min_max(corners2)
        return not (max_x1 < min_x2 or min_x1 > max_x2 or max_y1 < min_y2 or min_y1 > max_y2)

    return is_overlap(corners1, corners2)


def box_hits_pallet_border(box, pallet_width, pallet_height):
    x, y, width, height, angle = box.x, box.y, box.width, box.height, box.angle
    rotated_corners = get_rotated_bounds(x, y, width, height, angle)

    for corner in rotated_corners:
        if corner[0] < 0 or corner[0] > pallet_width or corner[1] < 0 or corner[1] > pallet_height:
            return True
    return False

#FN to draw pallet and boxes
def draw_pallet_and_boxes(pallet_width, pallet_height, boxes):
    global ax
    ax.clear()

    #Draw pallet
    ax.add_patch(plt.Rectangle((0, 0), pallet_width, pallet_height, edgecolor='black', facecolor='tan'))

    #Draw box
    for i, box in enumerate(boxes):
        x, y, width, height, angle, id = box.x, box.y, box.width, box.height, box.angle, box.id 
        overlap = any(i != j and boxes_overlap(box, other) for j, other in enumerate(boxes))
        hits_pallet_border = box_hits_pallet_border(box, pallet_width, pallet_height)
        edgecolor = 'red' if overlap or hits_pallet_border else 'blue'
        color = 'red' if i == selected_box else 'lightblue'  # Highlight the selected box in red

        #Box Rotation
        rect = plt.Rectangle((x, y), width, height, edgecolor=edgecolor, facecolor=color, picker=True)
        t = mtransforms.Affine2D().rotate_deg_around(x + width / 2, y + height / 2, angle) + ax.transData
        rect.set_transform(t)
        ax.add_patch(rect)  

        #Annotate box
        center_x = x + width / 2
        center_y = y + height / 2
        ax.text(center_x, center_y, str(id), color='black', fontsize=10, ha='center', va='bottom', rotation=0)
        ax.text(center_x, center_y, f'({center_x:.1f}, {center_y:.1f})', color='black', fontsize=8, ha='center', va='top', rotation=0)

    #Layers and number of pallets
    ax.text(pallet_width / 2, pallet_height + 5, f'Layer {current_layer + 1}', fontsize=12, ha='center', va='center', color='green')

    ax.set_xlim(0, pallet_width + 10)
    ax.set_ylim(0, pallet_height + 10)
    ax.set_aspect('equal')
    canvas.draw()
    # Khairul
    # return [center_x, center_y]

# FN to update Pallet
def update_canvas():
    global layers
    try:
        pallet_width = int(pallet_width_entry.get())
    except ValueError:
        print("Invalid input! Please enter a valid number.")
        pallet_width = 50  
    try:
        pallet_height = int(pallet_height_entry.get())
    except ValueError:
        print("Invalid input! Please enter a valid number.")
        pallet_height = 50  
    
    # TODO Khairul to add validation for pellet width/height
    # validate_pallet_width_input(pallet_width)
    # validate_pallet_height_input(pallet_height)

    draw_pallet_and_boxes(pallet_width, pallet_height, layers[current_layer])

# Event for Button press
def on_press(event):
    global dragging_box, offset_x, offset_y, selected_box
    if event.inaxes is not ax:
        return
    selected_box = None
    # for box in layers[current_layer]:
    for i, box in enumerate(layers[current_layer]):
        print(box)
        x, y, width, height, angle = box.x, box.y, box.width, box.height, box.angle
        center_x = x + width / 2
        center_y = y + height / 2

        transformed_x = event.xdata - center_x
        transformed_y = event.ydata - center_y
        rotated_x = transformed_x * np.cos(np.radians(angle)) + transformed_y * np.sin(np.radians(angle))
        rotated_y = -transformed_x * np.sin(np.radians(angle)) + transformed_y * np.cos(np.radians(angle))

        if -width / 2 <= rotated_x <= width / 2 and -height / 2 <= rotated_y <= height / 2:
            dragging_box = i
            selected_box = i
            offset_x = rotated_x
            offset_y = rotated_y
            break
    update_canvas()

# Event for mouse drag
# Works
def on_motion(event):
    global dragging_box
    if dragging_box is None:
        return
    if event.inaxes is not ax:
        return

    box = layers[current_layer][dragging_box]
    width, height, angle, id = box.width, box.height, box.angle, box.id

    center_x = event.xdata - offset_x
    center_y = event.ydata - offset_y

    new_x = center_x - width / 2
    new_y = center_y - height / 2

    # layers[current_layer][dragging_box] = Box(new_x, new_y, width, height, angle, id, current_layer)
    box.x = new_x
    box.y = new_y
    print(box)

    update_canvas()

# Event mouse release
def on_release(event):
    global dragging_box
    dragging_box = None

# FN for new box
def add_box():
    global layers
    angle = 0
    new_width = int(box_width_entry.get())
    new_height = int(box_height_entry.get())
    box_id = len(layers[current_layer]) + 1  

    new_box = Box(10, 10, new_width, new_height, box_id, angle, current_layer)
    layers[current_layer].append(new_box)
    print(new_box)

    update_canvas()

# FN delete box
def delete_box():
    global layers, selected_box
    if selected_box is not None:
        layers[current_layer] = [box for box in layers[current_layer] if box.id != selected_box]
        selected_box = None
        update_canvas()

# FN rotate box
def rotate_box():
    global layers, selected_box
    if selected_box is not None:
        x, y, width, height, angle = layers[current_layer][selected_box]
        layers[current_layer][selected_box] = (x, y, width, height, (angle + 15) % 360)
        update_canvas()

# FN jog box
def jog_box(dx, dy):
    global layers, selected_box
    if selected_box is not None:
        x, y, width, height, angle = layers[current_layer][selected_box]

        # apply jog data in global space relative to pallet
        layers[current_layer][selected_box] = (x + dx, y + dy, width, height, angle)
        update_canvas()

# FN for jogging buttons
def jog_up():
    distance = float(jog_distance_entry.get())
    jog_box(0, distance)

def jog_down():
    distance = float(jog_distance_entry.get())
    jog_box(0, -distance)

def jog_left():
    distance = float(jog_distance_entry.get())
    jog_box(-distance, 0)

def jog_right():
    distance = float(jog_distance_entry.get())
    jog_box(distance, 0)

# Fn switch to next layer
def next_layer():
    global current_layer
    if current_layer < len(layers) - 1:
        current_layer += 1
    update_canvas()

# Fn go to previous layer
def previous_layer():
    global current_layer
    if current_layer > 0:
        current_layer -= 1
    update_canvas()

# Fn add new layer
def add_layer():
    global layers, current_layer
    layers.append([])
    current_layer = len(layers) - 1
    update_canvas()

#Khairul 

def delete_layer():
    global layers, current_layer
    layers.pop(current_layer)
    current_layer = len(layers) - 1
    update_canvas()

# Test check list
def current_list_check():
    print(layers[current_layer])
    print(type(layers[current_layer]))
#Validate pallet width 
# def validate_pallet_width_input(pallet_width):
#     try:
#         if 50 <= pallet_width <= 500:  
#             return True
#         else:
#             return False
#     except ValueError:
#         return False
    
#Validate pallet width 
# def validate_pallet_height_input(pallet_height):
#     try:
#         if 50 <= pallet_height <= 500: 
#             return True
#         else:
#             return False
#     except ValueError:
#         return False

# IP Address
ttk.Label(root, text="Your IPV4 Address:").grid(row=IP_ADDRESS_1, column=COLUMN_0)
ip_address_entry = tk.Entry(root)
ip_address_entry.grid(row=IP_ADDRESS_1, column=COLUMN_1)
ip_address = get_ethernet_ip()
ip_address_entry.insert(0, f"{ip_address}")

# Connect to Robot 
ttk.Button(root, text="Connect", command=set_server_connection).grid(row=IP_ADDRESS_1, column=COLUMN_3)

# Server Connection status
server_label = ttk.Label(root, text="Server Status: Disconnected")
server_label.grid(row=IP_ADDRESS_1, column=COLUMN_2)

# Message updates
message_out_label = ttk.Label(root, text="Waiting for message to be sent")
message_out_label.grid(row=IP_ADDRESS_2, column=COLUMN_2)
message_queue = queue.Queue()

tk.Button(root, text="Check array", command=lambda: current_list_check()).grid(row=PALLET_WIDTH, column=COLUMN_2)


# Send data to Robot
# tk.Button(root, text="Send Data", command=lambda: send_to_robot("Hello from server!")).grid(row=IP_ADDRESS_2, column=COLUMN_3)
tk.Button(root, text="Send Data", command=lambda: send_to_robot()).grid(row=IP_ADDRESS_2, column=COLUMN_3)

# Pallet dimensions
ttk.Label(root, text="Pallet Width").grid(row=PALLET_WIDTH, column=COLUMN_0)
pallet_width_entry = tk.Entry(root)
pallet_width_entry.insert(0, "200")
pallet_width_entry.grid(row=PALLET_WIDTH, column=COLUMN_1)

ttk.Label(root, text="Pallet Height").grid(row=PALLET_HEIGHT, column=COLUMN_0)
pallet_height_entry = tk.Entry(root)
pallet_height_entry.insert(0, "200")
pallet_height_entry.grid(row=PALLET_HEIGHT, column=COLUMN_1)

# input box dimensions
ttk.Label(root, text="Box Width").grid(row=BOX_WIDTH, column=COLUMN_0)
box_width_entry = tk.Entry(root)
box_width_entry.insert(0, "50")
box_width_entry.grid(row=BOX_WIDTH, column=COLUMN_1)

ttk.Label(root, text="Box Height").grid(row=BOX_HEIGHT, column=COLUMN_0)
box_height_entry = tk.Entry(root)
box_height_entry.insert(0, "30")
box_height_entry.grid(row=BOX_HEIGHT, column=COLUMN_1)

# ttk.Button(root, text="Update Pallet", command=update_canvas).grid(row=PALLET_UPDATE, column=COLUMN_2)

ttk.Button(root, text="Add Box", command=add_box).grid(row=ADD_DELETE_BOX_ROW, column=COLUMN_0)
ttk.Button(root, text="Delete Box", command=delete_box).grid(row=ADD_DELETE_BOX_ROW, column=COLUMN_1)
ttk.Button(root, text="Rotate Box", command=rotate_box).grid(row=ROTATE_BOX, column=COLUMN_0)

ttk.Label(root, text="Jog Distance").grid(row=JOG_DISTANCE, column=COLUMN_0)
jog_distance_entry = tk.Entry(root)
jog_distance_entry.insert(0, "10")
jog_distance_entry.grid(row=JOG_DISTANCE, column=COLUMN_1)

ttk.Button(root, text="Jog Up", command=jog_up).grid(row=JOG_UP_RIGHT_ROW, column=COLUMN_0)
ttk.Button(root, text="Jog Right", command=jog_right).grid(row=JOG_UP_RIGHT_ROW, column=COLUMN_1)
ttk.Button(root, text="Jog Down", command=jog_down).grid(row=JOG_DOWN_LEFT_ROW, column=COLUMN_0)
ttk.Button(root, text="Jog Left", command=jog_left).grid(row=JOG_DOWN_LEFT_ROW, column=COLUMN_1)


# Button for layers
ttk.Button(root, text="Add Layer", command=add_layer).grid(row=ADD_DELETE_LAYER, column=COLUMN_0)
ttk.Button(root, text="Delete Layer", command=delete_layer).grid(row=ADD_DELETE_LAYER, column=COLUMN_1)
 
ttk.Button(root, text="Previous Layer", command=previous_layer).grid(row=NEXT_PREVIOUS_LAYER, column=COLUMN_0)
ttk.Button(root, text="Next Layer", command=next_layer).grid(row=NEXT_PREVIOUS_LAYER, column=COLUMN_1)


fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=GRID_LAYOUT, column=COLUMN_0, columnspan=COLUMN_2)


fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("motion_notify_event", on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)

# Bind the window close event to on_closing
root.protocol("WM_DELETE_WINDOW", lambda: on_closing(stop_event))  # Properly close when the window is closed
try:
    polling_mainloop()
except KeyboardInterrupt:
    print("Program interrupted, exiting gracefully...")
    root.quit()  # Ensure mainloop is stopped gracefully


# update_canvas()
root.mainloop()
