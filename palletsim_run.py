import tkinter as tk
from tkinter import ttk 
from tkinter.filedialog import asksaveasfilename, askopenfilename

import numpy as np

import time
import copy
import socket
import threading
import queue
import psutil

import json

import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from box import Box


## Condition for Testing purposes
robot_connected =  True

PORT = 50000
# Row / Col editing

# Row
SAVE_IMPORT_FILE = 0
IP_ADDRESS_1 = 1
IP_ADDRESS_2 = 2
PALLET_WIDTH = 3
PALLET_LENGTH = 4
PALLET_UPDATE = 5

BOX_WIDTH = 6
BOX_LENGTH = 7
BOX_HEIGHT = 8
ADD_DELETE_BOX_ROW = 9
ROTATE_VALUE = 10
ROTATE_BOX = 11

JOG_DISTANCE = 10
JOG_UP_RIGHT_ROW = 11
JOG_DOWN_LEFT_ROW = 12

ADD_DELETE_LAYER = 15
NEXT_PREVIOUS_LAYER = 16

GRID_LAYOUT = 17

# Column
COLUMN_0 = 0
COLUMN_1 = 1
COLUMN_2 = 2
COLUMN_3 = 3

dragging_box = None
selected_box = None
offset_x = 0
offset_y = 0
current_layer = 1

layers = [None, []]

ip_address_selection_val = None
curr_index_action_dropdown_val = None
curr_index_selection_dropdown_val = None
curr_allpose_action_dropdown_val = None

stop_event = threading.Event()
connection_established = False
client_connection = None

# main window
root = tk.Tk()
root.resizable(True, True)

root.title("Pallet and Boxes")

def on_closing(stop_event):
    """Handle the window closing event to stop the server thread."""
    # global stop_event
    if stop_event:
        stop_event.set()  # Signal the server thread to stop
    root.quit()  # Exit the mainloop

def polling_mainloop():
    # To review
    # Should update dropdown once after every action OR continuous polling (?) 
    # Most original functions in code are all currently updated after every action. This polling mainloop overrides.
    update_canvas()
    update_all_dropdown()
    root.after(1000, polling_mainloop)  # Keep checking the message queue every 100ms

# IP_dropdown1
def update_dropdown_ip(event):
    global ip_address_selection_val

    interfaces = list(psutil.net_if_addrs().keys())
    ethernet_interfaces = [ether for ether in interfaces if "Ethernet" in ether]

    ip_dropdown_selection['values'] = ethernet_interfaces
    ip_address_selection_val = ip_dropdown_selection.get()

def get_ethernet_ip():
    for interface, addrs in psutil.net_if_addrs().items():
        update_dropdown_ip(event=None)
        print(ip_address_selection_val)
        if ip_address_selection_val in interface:
            for addr in addrs:
                # Look for an IPv4 address
                if addr.family == socket.AF_INET:
                    print(f"Found IP: {addr.address}")  # Debugging line to show found IP
                    print(f"PORT: {PORT}")
                    return addr.address
                else:
                    print("Check your ethernet connection")

def server_thread_func(stop_event):
    global connection_established, client_connection

    
    IP_ADDRESS = get_ethernet_ip()
    
    while not stop_event.is_set():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
            
            try:
                sock.bind((IP_ADDRESS, PORT)) 
                sock.listen()
                
                print(type(IP_ADDRESS))
                # print (f"Server listening on {IP_ADDRESS}:{PORT}")    
                server_label.config(text="Server Status: Connected")

                conn, addr = sock.accept()
                client_connection = conn
                connection_established = True
                update_gui_from_server
                        
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

###
def send_and_wait_for_response(client_connection, data_to_send):
    # Debug
    if client_connection.fileno() == -1:
        print("Socket is invalid or closed.")
        return None
    data_to_send = data_to_send[0]
    data_to_send = str(data_to_send).replace("[", "(").replace("]", ")") + '\n'
    
    client_connection.sendall(data_to_send.encode('utf-8'))

    print(f"Sent: {data_to_send}")

    # Debug
    if client_connection.fileno() == -1:
        print("Socket is invalid or closed.")
        return None
    else:
        print("SOCKET IS OPEN AND READY TO GO")
    
        print("im here")
        client_connection.recv(1024).decode('utf-8')

# Unused
def threaded_send_and_wait(client_connection, data):
    response = send_and_wait_for_response(client_connection, data)
    if response:
        print("Response received, proceeding to next box.")
    else:
        print("No response received, skipping box.")
    
def send_all_pose_to_robot():
    global connection_established, client_connection

    # print(allpose_action_index)
    print("Button execute check")
    print(connection_established)
    print(client_connection) 
    
    if connection_established and client_connection:
        print("established")
        print(curr_allpose_action_dropdown_val)
        if curr_allpose_action_dropdown_val == 1:
            try:
                for box in layers[current_layer]:
                    print("Layer send check")
                    data_list = []
                    box_id = box.id
                    box_angle = box.angle
                    box_height = box.height
                    box_layer = box.layer
                    box_center_x = float(round(box.x + box.width / 2, 2))
                    box_center_y = float(round(box.y + box.length / 2, 2))
                    count = len(layers[current_layer])

                    print("Total number of Boxes in this layer: " + str(count))
                    data_list.append([count, box_id, (box_center_x/1000), (box_center_y/1000), box_angle, ((box_height+ 20)/1000), box_layer])

                    print("DATA LIST")
                    print(data_list)

                    send_and_wait_for_response(client_connection, data_list)

            except Exception as e:
                print(f"Error sending data: {str(e)}")
                update_server_status("Server Status: (Error) Failed to send data")

        elif curr_allpose_action_dropdown_val == 2:
            try:
                all_boxes = [box for boxes in layers if boxes is not None for box in boxes]
                count = len(all_boxes)
                print("All pose send check")
                if current_layer >= len(layers) or layers[current_layer] is None:
                    print(f"Invalid current_layer index: {current_layer}")
                    
                for layer_index, layer in enumerate(layers):
                    if layer is None:
                        continue
                    for box in layer:
                        print("Data_send")
                        data_list = []
                        box_id = box.id
                        box_angle = box.angle
                        box_height = box.height
                        box_layer = box.layer
                        box_center_x = float(round(box.x + box.width / 2, 2))
                        box_center_y = float(round(box.y + box.length / 2, 2))

                        print(f"Sending pose for box({box_id}) in layer {layer_index}")
                        print("Total number of Boxes in all layers: " + str(count))
                        data_list.append([
                            count,
                            box_id,
                            (box_center_x / 1000),
                            (box_center_y / 1000),
                            box_angle,
                            ((box_height + 20) / 1000),
                            box_layer
                        ])
                        
                        print("DATA LIST")
                        print(data_list)
                        send_and_wait_for_response(client_connection, data_list)                  

            except Exception as e:
                print(f"Error sending data: {str(e)}")
                update_server_status("Server Status: (Error) Failed to send data")

# Testing
def no_connection_send_all_pose_to_robot():
    print("Send_all_check")
    if curr_allpose_action_dropdown_val == 1:
            for box in layers[current_layer]:
                print("Layer send check")
                data_list = []
                count = len(layers[current_layer])

                box_id = box.id
                box_angle = box.angle
                box_height = box.height
                box_layer = box.layer
                box_center_x = float(round(box.x + box.width / 2, 2))
                box_center_y = float(round(box.y + box.length / 2, 2))
                
                print("Total number of Boxes in this layer: " + str(count))
                data_list.append([count, box_id, (box_center_x/1000), (box_center_y/1000), box_angle, ((box_height+ 20)/1000), box_layer])

                print("Box_Data_List")
                print(data_list)

    elif curr_allpose_action_dropdown_val == 2:
            all_boxes = [box for boxes in layers if boxes is not None for box in boxes]
            count = len(all_boxes)
            print("All pose send check")
            if current_layer >= len(layers) or layers[current_layer] is None:
                print(f"Invalid current_layer index: {current_layer}")
                
            for layer_index, layer in enumerate(layers):
                if layer is None:
                    continue
                for box in layer:
                    data_list = []
                    box_id = box.id
                    box_angle = box.angle
                    box_height = box.height
                    box_layer = box.layer
                    box_center_x = float(round(box.x + box.width / 2, 2))
                    box_center_y = float(round(box.y + box.length / 2, 2))

                    print(f"Sending pose for box in layer {layer_index}")
                    print("Total number of Boxes in all layers: " + str(count))
                    data_list.append([
                        count,
                        box_id,
                        (box_center_x / 1000),
                        (box_center_y / 1000),
                        box_angle,
                        ((box_height + 20) / 1000),
                        box_layer
                    ])

                print("DATA LIST")
                print(data_list)

def send_selected_pose_to_robot():
    global connection_established, client_connection, curr_index_selection_dropdown_val
    print("Robot Connection. Selected execute check")
    curr_index_selection_dropdown_val = int(curr_index_selection_dropdown_val)
    
    if connection_established and client_connection:
        if curr_index_action_dropdown_val == 1:
            try:
                for box in layers[current_layer]:
                    if box.id == curr_index_selection_dropdown_val:
                        data_list = []
                        count = len(layers[current_layer])
                        box_id = box.id
                        box_angle = box.angle
                        box_height = box.height
                        box_layer = box.layer
                        box_center_x = float(round(box.x + box.width / 2, 2))
                        box_center_y = float(round(box.y + box.length / 2, 2))
                        
                        data_list.append([count, box_id, (box_center_x/1000), (box_center_y/1000), box_angle, ((box_height+ 20)/1000), box_layer])

                        print("DATA LIST")
                        print(data_list)

                        send_and_wait_for_response(client_connection, data_list)

            except Exception as e:
                print(f"Error sending data: {str(e)}")
                update_server_status("Server Status: (Error) Failed to send data")

        elif curr_index_action_dropdown_val == 2:
            try:
                for box in layers[current_layer]:
                    if box.id >= curr_index_selection_dropdown_val:
                        data_list = []
                        count = len(layers[current_layer])
                        box_id = box.id
                        box_angle = box.angle
                        box_height = box.height
                        box_layer = box.layer
                        box_center_x = float(round(box.x + box.width / 2, 2))
                        box_center_y = float(round(box.y + box.length / 2, 2))
                        
                        data_list.append([count, box_id, (box_center_x/1000), (box_center_y/1000), box_angle, ((box_height+ 20)/1000), box_layer])

                        print("DATA LIST")
                        print(data_list)

                        send_and_wait_for_response(client_connection, data_list)

            except Exception as e:
                print(f"Error sending data: {str(e)}")
                update_server_status("Server Status: (Error) Failed to send data")
#Testing
def no_connection_send_selected_pose_to_robot():
    global curr_index_selection_dropdown_val
    print("Selected execute check")
    curr_index_selection_dropdown_val = int(curr_index_selection_dropdown_val)

    if curr_index_action_dropdown_val == 1:
        for box in layers[current_layer]:
            print(type(box.id))
            if box.id == curr_index_selection_dropdown_val:
                data_list = []
                count = len(layers[current_layer])
                box_id = box.id
                box_angle = box.angle
                box_height = box.height
                box_layer = box.layer
                box_center_x = float(round(box.x + box.width / 2, 2))
                box_center_y = float(round(box.y + box.length / 2, 2))
                
                data_list.append([count, box_id, (box_center_x/1000), (box_center_y/1000), box_angle, ((box_height+ 20)/1000), box_layer])

                print("DATA LIST")
                print(data_list)
                time.sleep(1)


    elif curr_index_action_dropdown_val == 2:
            for box in layers[current_layer]:
                print(type(box.id))
                if box.id >= curr_index_selection_dropdown_val:
                    data_list = []
                    count = len(layers[current_layer])
                    box_id = box.id
                    box_angle = box.angle
                    box_height = box.height
                    box_layer = box.layer
                    box_center_x = float(round(box.x + box.width / 2, 2))
                    box_center_y = float(round(box.y + box.length / 2, 2))
                    
                    data_list.append([count, box_id, (box_center_x/1000), (box_center_y/1000), box_angle, ((box_height+ 20)/1000), box_layer])

                    print("DATA LIST")
                    print(data_list)
                    time.sleep(1)
                     
### Save and Import
def save_file():
    print("Saving current Palletizing template data...")
    data_list = []
    box_counter = 0 
    
    for i in range(len(layers)): 
        layer_has_boxes = False

        for box in layers[i] or []:
            layer_has_boxes = True
            box_counter += 1
            box_data = {
                "layer_has_boxes": True,
                "box_counter": box_counter,
                "box_id": box.id,
                "box_x": box.x,
                "box_y": box.y,
                "box_width": box.width,
                "box_length": box.length,
                "angle": box.angle,
                "height_val": box.height,
                "layer": box.layer   
            }
            data_list.append(box_data)
        
        if not layer_has_boxes:
            box_data = {
                "layer_has_boxes": False,
                "box_counter": box_counter,
                "box_id": "NIL",
                "box_x": "NIL",
                "box_y": "NIL",
                "box_width": "NIL",
                "box_length": "NIL",
                "angle": "NIL",
                "height_val": "NIL",
                "layer": i
            }
            data_list.append(box_data)
    
    file_path = asksaveasfilename(
    defaultextension=".json",
    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    title="Save Palletizing Data As..."
    )
    
    if not file_path:
        print("Save cancelled.")
        return
    
    with open(file_path, "w") as file:
        json.dump(data_list, file, indent=4)

    print(f"File saved to {file_path}")
    
    
def import_file():
    global layers, current_layer

    print("Select file to import")
    
    file_path = askopenfilename(
    title="Select a PalletSim JSON file",
    filetypes=[("JSON files", "*.json")]
    )

    if file_path:
        with open(file_path, "r") as f:
            data = json.load(f)

        print("Loaded JSON data:")
        layers = []
        for entry in data:
            layer_val = entry["layer"]
            layer_has_boxes = entry["layer_has_boxes"]

            while len(layers) <= layer_val:
                layers.append([])

            if layer_has_boxes:
                # If the layer currently None, replace with empty list
                if layers[layer_val] is None:
                    layers[layer_val] = []
 
                box_counter = entry["box_counter"]
                box_id = entry["box_id"]
                box_x = entry["box_x"]
                box_y = entry["box_y"]
                box_width = entry["box_width"]
                box_length = entry["box_length"]
                angle = entry["angle"]
                height_val = entry["height_val"]

                new_box = Box(box_x, 
                            box_y,
                            box_width,
                            box_length, 
                            height_val, 
                            box_id, 
                            angle, 
                            layer_val)            

                layers[layer_val].append(new_box)
                print(layers)

            else:
                # Keep layer as None if no boxes
                layers[layer_val] = []

    current_layer = 1
    update_canvas()


def get_rotated_bounds(x, y, width, length, angle):
    angle_rad = np.radians(angle)
    cx, cy = x + width / 2, y + length / 2
    corners = np.array([
        [x, y],
        [x + width, y],
        [x + width, y + length],
        [x, y + length]
    ]) - [cx, cy]
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])
    rotated_corners = (corners @ rotation_matrix.T) + [cx, cy]
    return rotated_corners


def boxes_overlap(box1, box2):
    corners1 = get_rotated_bounds(box1.x, box1.y, box1.width, box1.length, box1.angle)
    corners2 = get_rotated_bounds(box2.x, box2.y, box2.width, box2.length, box2.angle)

    def min_max(corners):
        return (np.min(corners[:, 0]), np.max(corners[:, 0]), np.min(corners[:, 1]), np.max(corners[:, 1]))

    def is_overlap(corners1, corners2):
        min_x1, max_x1, min_y1, max_y1 = min_max(corners1)
        min_x2, max_x2, min_y2, max_y2 = min_max(corners2)
        return not (max_x1 < min_x2 or min_x1 > max_x2 or max_y1 < min_y2 or min_y1 > max_y2)

    return is_overlap(corners1, corners2)


def box_hits_pallet_border(box, pallet_width, pallet_length):
    x, y, width, length, angle = box.x, box.y, box.width, box.length, box.angle
    rotated_corners = get_rotated_bounds(x, y, width, length, angle)

    for corner in rotated_corners:
        if corner[0] < 0 or corner[0] > pallet_width or corner[1] < 0 or corner[1] > pallet_length:
            return True
    return False

#FN to draw pallet and boxes
def draw_pallet_and_boxes(pallet_width, pallet_length, boxes):
    global ax
    
    width_fig_scale = 2
    length_fig_scale = 10

    ax.clear()
    
    #Draw pallet
    ax.add_patch(plt.Rectangle((0, 0), pallet_width, pallet_length, edgecolor='black', facecolor='tan'))

    #Draw box
    for box in boxes:
        x, y, width, length, angle, id = box.x, box.y, box.width, box.length, box.angle, box.id 
        overlap = any(box.id != other.id and boxes_overlap(box, other) for other in boxes)
        hits_pallet_border = box_hits_pallet_border(box, pallet_width, pallet_length)
        edgecolor = 'red' if overlap or hits_pallet_border else 'blue'
        color = 'red' if box.id == selected_box else 'lightblue'  # Highlight the selected box in red

        #Box Rotation
        rect = plt.Rectangle((x, y), width, length, edgecolor=edgecolor, facecolor=color, picker=True)
        t = mtransforms.Affine2D().rotate_deg_around(x + width / 2, y + length / 2, angle) + ax.transData
        rect.set_transform(t)
        ax.add_patch(rect)  

        #Annotate box
        center_x = x + width / 2
        center_y = y + length / 2
        line_spacing = 4

        ax.text(center_x, center_y + line_spacing, str(id), color='black', fontsize=9, ha='center', va='bottom', rotation=0)
        ax.text(center_x, center_y, f'({center_x:.1f}, {center_y:.1f})', color='black', fontsize=8, ha='center', va='center', rotation=0)
        ax.text(center_x, center_y - line_spacing, f'({box.angle:.1f})', color='black', fontsize=8, ha='center', va='top', rotation=0)

    #Layers and number of pallets
    ax.text(pallet_width / 2, pallet_length + 5, f'Layer {current_layer}', fontsize=12, ha='center', va='center', color='green')

    ax.set_xlim(0, pallet_width + (pallet_width / width_fig_scale))
    ax.set_ylim(0, pallet_length + (pallet_length / length_fig_scale))
    ax.set_aspect('equal')
    canvas.draw()

# FN to update Pallet
def update_canvas():
    global layers, pallet_width, pallet_length
    try:
        pallet_width = int(pallet_width_entry.get())
    except ValueError:
        print("Invalid input! Please enter a valid number.")
        pallet_width = 50  
    try:
        pallet_length = int(pallet_length_entry.get())
    except ValueError:
        print("Invalid input! Please enter ,m a valid number.")
        pallet_length = 50  
    update_all_dropdown()
    draw_pallet_and_boxes(pallet_width, pallet_length, layers[current_layer])

    return pallet_width, pallet_length
    
# Event for Button press
def on_press(event):
    global dragging_box, offset_x, offset_y, selected_box
    if event.inaxes is not ax:
        return
    selected_box = None
    for i, box in enumerate(layers[current_layer]):
        print(box)
        x, y, width, length, angle = box.x, box.y, box.width, box.length, box.angle
        center_x = x + width / 2
        center_y = y + length / 2

        transformed_x = event.xdata - center_x
        transformed_y = event.ydata - center_y
        rotated_x = transformed_x * np.cos(np.radians(angle)) + transformed_y * np.sin(np.radians(angle))
        rotated_y = -transformed_x * np.sin(np.radians(angle)) + transformed_y * np.cos(np.radians(angle))

        if -width / 2 <= rotated_x <= width / 2 and -length / 2 <= rotated_y <= length / 2:
            dragging_box = i
            selected_box = box.id
            offset_x = rotated_x
            offset_y = rotated_y
            break
    update_canvas()

# Event for mouse drag
def on_motion(event):
    global dragging_box
    if dragging_box is None:
        return
    if event.inaxes is not ax:
        return

    box = layers[current_layer][dragging_box]
    width, length = box.width, box.length

    center_x = event.xdata - offset_x
    center_y = event.ydata - offset_y

    new_x = center_x - width / 2
    new_y = center_y - length / 2

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
    new_length = int(box_length_entry.get())

    box_id = len(layers[current_layer]) + 1 # + 1 because it starts from 0 instead of 1

    if current_layer > 1:
            try:
                max_height = max(
                    box.height for layer in layers[:current_layer] if layer 
                       for box in layer if box
        )
            except ValueError:
                max_height = 0
            
            new_height = int(box_height_entry.get()) + max_height

    else:
        new_height = int((box_height_entry.get()))

    new_box = Box(pallet_width + 5, 10, new_width, new_length, new_height, box_id, angle, current_layer)
    layers[current_layer].append(new_box)
    print(new_box)
    print(layers)    
    update_canvas()

# FN delete box
def delete_box():
    global layers, selected_box
    print(selected_box)
    if selected_box is not None:
        layers[current_layer] = [box for box in layers[current_layer] if box.id != selected_box]

        for index, box in enumerate(layers[current_layer], start=1):
            box.id = index  # Reassign sequential IDs based on index

        selected_box = None
        update_canvas()
        

# FN rotate box
def rotate_box_anticlockwise():
    global layers, selected_box
    new_angle = float(box_angle_entry.get())

    if selected_box is not None:
        for box in layers[current_layer]:
            if box.id == selected_box:
                box.angle =  (box.angle + new_angle) % 360
                
                update_canvas()

def rotate_box_clockwise():
    global layers, selected_box
    new_angle = float(box_angle_entry.get())

    if selected_box is not None:
        for box in layers[current_layer]:
            if box.id == selected_box:
                box.angle =  (box.angle - new_angle) % 360

                update_canvas()

# FN jog box
def jog_box(dx, dy):
    global layers, selected_box
    if selected_box is not None:
        for box in layers[current_layer]:
            if box.id == selected_box:
                box.x = box.x + dx
                box.y = box.y + dy
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
    else:
        print("This is the lowest layer")
    
    update_canvas()

# Fn add new layer
def add_layer():
    global layers, current_layer

    layers.append([])
    current_layer = len(layers) - 1
    print(layers)
    update_canvas()

def delete_layer():
    global layers, current_layer

    layers.pop(current_layer)
    current_layer = len(layers) - 1
    print(layers[current_layer])
    update_canvas()

# Duplicate current layer
def duplicate_current_layer():
    global layers, current_layer
    layers.append(copy.deepcopy(layers[current_layer]))

    current_layer = len(layers) - 1
    print(layers[current_layer])  # See what's in the layer
    print(len(layers))

    update_canvas()

# Test check list
def current_list_check():
    print(layers[current_layer])  # See what's in the layer
    print(str(layers[current_layer]) + "Box Midpoints")
    print(type(layers[current_layer]))

def update_all_dropdown():
    update_index_dropdown_selection(event=None)
    update_index_dropdown_action(event=None)
    update_allpose_dropdown_action(event=None)
    # update_layer_dropdown_selection(event=None)
    update_dropdown_ip(event=None)
    
def update_allpose_dropdown_action(event):
    global curr_allpose_action_dropdown_val

    allpose_dropdown_action['values'] = ['This layer only', 'All layers']
    allpose_dropdown_action_val = allpose_dropdown_action.get()

    if allpose_dropdown_action_val == 'This layer only':
            curr_allpose_action_dropdown_val = 1

    elif allpose_dropdown_action_val == 'All layers':
            curr_allpose_action_dropdown_val = 2

def update_index_dropdown_action(event):
    global curr_index_action_dropdown_val
    
    box_index_dropdown_action['values'] = ['Selected box only', 'Selected box onwards']
    index_selected_action = box_index_dropdown_action.get()


    if index_selected_action == 'Selected box only':
            curr_index_action_dropdown_val = 1
    elif index_selected_action == 'Selected box onwards':
            curr_index_action_dropdown_val = 2
            
def update_index_dropdown_selection(event):
    global curr_index_selection_dropdown_val

    box_ids = [box.id for box in layers[current_layer]]
    if not box_ids:
        # update_server_status(f"No boxes found in layer {current_layer}")
        box_index_dropdown_selection['values'] = ["Select box index"]
        box_index_dropdown_selection.set("Select box index")

        # This is the problem. Demo2, curr_index_selection_dropdown_val is str. Either update the value to 1 whenever a new box is added or figureout a way to update the Str to int      
    box_index_dropdown_selection['values'] = [box.id for box in layers[current_layer]]  # Updated values
    curr_index_selection_dropdown_val = box_index_dropdown_selection.get()

# TODO
# def update_layer_dropdown_selection(event):
#     available_layers = []

#     for index, layer in enumerate(layers):
#         if index == current_layer or (layer is not None and len(layer) > 0):
#             available_layers.append(index)

#     # Update the dropdown values
#     layer_dropdown_selection['values'] = available_layers

#     # Set the dropdown to show the current layer
#     if current_layer in available_layers:
#         layer_dropdown_selection.set(current_layer)
#         layer_dropdown_selection.get()
#     else:
#         layer_dropdown_selection.set('')  # Clear if not valid

### GUI Buttons ###

# Col seperator
separator = tk.Frame(root, width=1, bg="black", relief='flat')
separator.grid(row=IP_ADDRESS_1, column=COLUMN_1, rowspan=9, sticky='nse', padx=(0, 0))
# Row seperator
separator = tk.Frame(root, height=1, bd=0, bg="black", relief='flat')
separator.grid(row=PALLET_WIDTH, column=COLUMN_0, columnspan=2, sticky='new', pady=(0, 0))
separator = tk.Frame(root, height=1, bd=0, bg="black", relief='flat')
separator.grid(row=BOX_WIDTH, column=COLUMN_0, columnspan=2, sticky='new', pady=(0, 0))
separator = tk.Frame(root, height=1, bd=0, bg="black", relief='flat')
separator.grid(row=JOG_DISTANCE, column=COLUMN_2, columnspan=2, sticky='new', pady=(0, 0))
separator = tk.Frame(root, height=1, bd=0, bg="black", relief='flat')
separator.grid(row=ADD_DELETE_LAYER, column=COLUMN_0, columnspan=4, sticky='new', pady=(0, 0))

# Button for Save and Import
ttk.Button(root, text="Save File", command=save_file).grid(row=SAVE_IMPORT_FILE, column=COLUMN_0)  
ttk.Button(root, text="Import File", command=import_file).grid(row=SAVE_IMPORT_FILE, column=COLUMN_1)  

# Button for IP Address and IP_dropdown
ttk.Label(root, text="Select the Ethernet Port: ").grid(row=IP_ADDRESS_1, column=COLUMN_0)
ip_dropdown_selection = ttk.Combobox(root)
ip_dropdown_selection.grid(row=IP_ADDRESS_1, column=COLUMN_1)
ip_dropdown_selection.bind("<<ComboboxSelected>>", update_dropdown_ip)


# Connect to Robot 
ttk.Button(root, text="Connect", command=set_server_connection).grid(row=IP_ADDRESS_1, column=COLUMN_3)  

# Server Connection status
server_label = ttk.Label(root, text="Server Status: Disconnected")
server_label.grid(row=IP_ADDRESS_1, column=COLUMN_2)

# Message updates
message_out_label = ttk.Label(root, text="Waiting for message to be sent")
message_out_label.grid(row=IP_ADDRESS_2, column=COLUMN_2)
message_queue = queue.Queue()

#temp
# tk.Button(root, text="[Temp] Check array", command=lambda: current_list_check()).grid(row=GRID_LAYOUT, column=COLUMN_3)

############
# Send all pallet pose to Robot

ttk.Label(root, text="Action for Box Layers").grid(row=PALLET_WIDTH, column=COLUMN_2)
allpose_dropdown_action = ttk.Combobox(root)
allpose_dropdown_action.grid(row=PALLET_WIDTH, column=COLUMN_3)
allpose_dropdown_action.bind("<<ComboboxSelected>>", update_allpose_dropdown_action)


tk.Button(root, text="Execute Box Layers Action", 
          command=lambda: send_all_pose_to_robot() if robot_connected else no_connection_send_all_pose_to_robot()).grid(row=PALLET_LENGTH, column=COLUMN_3)

# User selection for 1 box pose only or from box pose onwards 
## Box selection drop down
ttk.Label(root, text="Select Box Index").grid(row=BOX_WIDTH, column=COLUMN_2)
box_index_dropdown_selection = ttk.Combobox(root)
box_index_dropdown_selection.grid(row=BOX_LENGTH, column=COLUMN_2)

box_index_dropdown_selection.bind("<<ComboboxSelected>>", update_index_dropdown_selection)

## Action for Box selection
ttk.Label(root, text="Action for Box Index").grid(row=BOX_WIDTH, column=COLUMN_3)
box_index_dropdown_action = ttk.Combobox(root)
box_index_dropdown_action.grid(row=BOX_LENGTH, column=COLUMN_3)

box_index_dropdown_action.bind("<<ComboboxSelected>>", update_index_dropdown_action)

tk.Button(root, text="Execute Box Index Action", 
          command=lambda: send_selected_pose_to_robot() if robot_connected else no_connection_send_selected_pose_to_robot()).grid(row=BOX_HEIGHT, column=COLUMN_3)

############
# Pallet dimensions
ttk.Label(root, text="Pallet Width").grid(row=PALLET_WIDTH, column=COLUMN_0, padx=10, pady=5)
pallet_width_entry = tk.Entry(root)
pallet_width_entry.insert(0, "200")
pallet_width_entry.grid(row=PALLET_WIDTH, column=COLUMN_1, padx=10, pady=5)

ttk.Label(root, text="Pallet length").grid(row=PALLET_LENGTH, column=COLUMN_0)
pallet_length_entry = tk.Entry(root)
pallet_length_entry.insert(0, "200")
pallet_length_entry.grid(row=PALLET_LENGTH, column=COLUMN_1)


## Box Related ##

## Add/Delete Box
ttk.Button(root, text="Add Box", command=add_box).grid(row=ADD_DELETE_BOX_ROW, column=COLUMN_0)
ttk.Button(root, text="Delete Box", command=delete_box).grid(row=ADD_DELETE_BOX_ROW, column=COLUMN_1)

# Input box dimensions
ttk.Label(root, text="Box Width").grid(row=BOX_WIDTH, column=COLUMN_0, padx=10, pady=5)
box_width_entry = tk.Entry(root)
box_width_entry.insert(0, "50")
box_width_entry.grid(row=BOX_WIDTH, column=COLUMN_1, padx=10, pady=5)

ttk.Label(root, text="Box Length").grid(row=BOX_LENGTH, column=COLUMN_0)
box_length_entry = tk.Entry(root)
box_length_entry.insert(0, "30")
box_length_entry.grid(row=BOX_LENGTH, column=COLUMN_1)

ttk.Label(root, text="Box Height").grid(row=BOX_HEIGHT, column=COLUMN_0)
box_height_entry = tk.Entry(root)
box_height_entry.insert(0, "30")
box_height_entry.grid(row=BOX_HEIGHT, column=COLUMN_1)

## Manual Jogging
ttk.Label(root, text="Jog Distance").grid(row=JOG_DISTANCE, column=COLUMN_0)
jog_distance_entry = tk.Entry(root)
jog_distance_entry.insert(0, "10")
jog_distance_entry.grid(row=JOG_DISTANCE, column=COLUMN_1, padx=10, pady=5)

ttk.Button(root, text="Jog Up", command=jog_up).grid(row=JOG_UP_RIGHT_ROW, column=COLUMN_0)
ttk.Button(root, text="Jog Right", command=jog_right).grid(row=JOG_UP_RIGHT_ROW, column=COLUMN_1)
ttk.Button(root, text="Jog Down", command=jog_down).grid(row=JOG_DOWN_LEFT_ROW, column=COLUMN_0)
ttk.Button(root, text="Jog Left", command=jog_left).grid(row=JOG_DOWN_LEFT_ROW, column=COLUMN_1)

# TODO
# ttk.Button(root, text="Flush_all_boxes_left", command=flush_all_boxes_left).grid(row=JOG_DOWN_LEFT_ROW, column=COLUMN_1)
# ttk.Button(root, text="Flush_all_boxes_bottom", command=flush_all_boxes_bottom).grid(row=JOG_DOWN_LEFT_ROW, column=COLUMN_1)

# Button for Box Rotation
ttk.Label(root, text="Rotation Value (deg)").grid(row=ROTATE_VALUE, column=COLUMN_2)
box_angle_entry = tk.Entry(root)
box_angle_entry.insert(0, "10")
box_angle_entry.grid(row=ROTATE_VALUE, column=COLUMN_3)
ttk.Button(root, text="Rotate Box Anti-clockwise", command=rotate_box_anticlockwise).grid(row=ROTATE_BOX, column=COLUMN_2)
ttk.Button(root, text="Rotate Box Clockwise", command=rotate_box_clockwise).grid(row=ROTATE_BOX, column=COLUMN_3)


# Button for layers
ttk.Button(root, text="Add Layer", command=add_layer).grid(row=ADD_DELETE_LAYER, column=COLUMN_0, padx=10, pady=5)
ttk.Button(root, text="Delete Layer", command=delete_layer).grid(row=ADD_DELETE_LAYER, column=COLUMN_1, padx=10, pady=5)
ttk.Button(root, text="Previous Layer", command=previous_layer).grid(row=NEXT_PREVIOUS_LAYER, column=COLUMN_0)
ttk.Button(root, text="Next Layer", command=next_layer).grid(row=NEXT_PREVIOUS_LAYER, column=COLUMN_1)
ttk.Button(root, text="Duplicate Current Layer", command=duplicate_current_layer).grid(row=NEXT_PREVIOUS_LAYER, column=COLUMN_2)

# TODO
## Layer selection drop down
# ttk.Label(root, text="Select Box Index").grid(row=BOX_WIDTH, column=COLUMN_2)
# layer_dropdown_selection = ttk.Combobox(root)
# layer_dropdown_selection.grid(row=ADD_DELETE_LAYER, column=COLUMN_2)

# layer_dropdown_selection.bind("<<ComboboxSelected>>", update_layer_dropdown_selection)

fig, ax = plt.subplots(figsize=(10, 6))
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


update_canvas()
root.mainloop()
