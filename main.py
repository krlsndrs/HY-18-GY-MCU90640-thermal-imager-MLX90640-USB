import serial, time
import datetime as dt
import numpy as np
import cv2
import binascii

# function to get Emissivity from MCU
def get_emissivity():
	ser.write(serial.to_bytes([0xA5,0x55,0x01,0xFB]))
	read = ser.read(4)
	return read[2]/100

# function to get temperatures from MCU (Celsius degrees x 100)
def get_temp_array(d):

	# getting ambient temperature
	T_a = (int(d[1540]) + int(d[1541])*256)/100

	# getting raw array of pixels temperature
	raw_data = d[4:1540]
	T_array = np.frombuffer(raw_data, dtype=np.int16)
	
	return T_a, T_array

# function to convert temperatures to pixels on image
def td_to_image(f):
	norm = np.uint8((f/100 - Tmin)*255/(Tmax-Tmin))
	norm.shape = (24,32)
	return norm

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect
	
def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

def sincronizar():
        miFrameNoDetectado = True
        while miFrameNoDetectado:
            try:
              read_byte = ser.read(1)
              #print (type( read_byte ))
              #print ( binascii.hexlify(bytearray(read_byte)) )
              if ( bytearray(read_byte)[0] == 0x5a): 
                print ("Encontre el inicio...")
                
                read_byte = ser.read(3)
                print ( binascii.hexlify(bytearray(read_byte)) )
                if ( bytearray(read_byte)[0] == 0x5a  and bytearray(read_byte)[1] == 0x02 and bytearray(read_byte)[2] == 0x06): 
                  print ("Encontre el header restante")
                  miFrameNoDetectado = False
                  break
                else:
                  #time.sleep(1)
                  continue
            except KeyboardInterrupt:
                print("Keyboard Interrupt")
                break  
        print ("Frame Header  encontrado") 
        ata = ser.read(1540) # Descarto el primer cuadro

########################### Main cycle #################################
capture = cv2.VideoCapture(0)
#-100 0 50 0 -150 150 50 150
mostrarCamara = True
modoEspejo = True
a = -70
b = 30
c = 20
d = 0
e = -150
f = 150
g = 50
h = 150

# Color map range
Tmax = 38
Tmin = 23
rangoDinamico = True
gaussianEnfoque = False
colorMap = 20
interpolacion = 3

print ('Configuring Serial port')
#ser = serial.Serial ('/dev/serial0')
#ser.baudrate = 115200

ser = serial.Serial ('/dev/ttyUSB0')
ser.baudrate = 115200


# set frequency of module to 4 Hz
ser.write(serial.to_bytes([0xA5,0x25,0x01,0xCB]))
time.sleep(0.1)

# Starting automatic data colection
ser.write(serial.to_bytes([0xA5,0x35,0x02,0xDC]))
t0 = time.time()


# Primera captura de datos        
sincronizar() 


try:
	while True:
		# waiting for data frame
		data = ser.read(1544)
		
		# Comprobar que se ha capturado el header
		if not( bytearray(data)[0] == 0x5a and 
		     bytearray(data)[1] == 0x5a and 
		     bytearray(data)[2] == 0x02 and
		     bytearray(data)[3] == 0x06     ): 
		        print ("Resincronizando !")
		        sincronizar()
		        continue

		
		
		# The data is ready, let's handle it!
		Ta, temp_array = get_temp_array(data)
		ta_img = td_to_image(temp_array)
		
		# Image processing
		img = cv2.applyColorMap(ta_img, colorMap) #cv2.COLORMAP_JET
		img = cv2.resize(img, (800,600), interpolation = interpolacion)#cv2.INTER_LANCZOS4 cv2.INTER_CUBIC cv2.INTER_AREA
		img = cv2.flip(img, 1)

		incremento = 15
		# Mascara de enfoque
		if gaussianEnfoque:
		        im_blurred = cv2.GaussianBlur(img, (11,11), 10)
		        img = cv2.addWeighted(img, 1.5, im_blurred, -0.5, 0, img)
		

		ret, webcam = capture.read()
		if ret and mostrarCamara:
		        webcam = cv2.resize(webcam,(800, 600))
		        gris = cv2.cvtColor(webcam, cv2.COLOR_BGR2GRAY)
		        gaussiana = cv2.GaussianBlur(gris, (5,5), 0)
		        edges =  cv2.Canny(gaussiana,50,150)
		        edges = cv2.cvtColor(edges,cv2.COLOR_GRAY2RGB)
		        webcam = cv2.addWeighted(webcam, 1, edges, 1, 0)
		        webcam = four_point_transform(webcam,  np.array([(0+a, 0+b), (800+c, 0+d), (0+e, 600+f), (800+g, 600+h)], dtype = "float32") )
		        webcam = cv2.resize(webcam,(800, 600))
#		        print(webcam.shape)
		        img =cv2.addWeighted(webcam, 0.3, img, 0.9, 0)
		        
	        #Recortar
		y=0
		x=150
		altura=485
		anchura=615
		if  mostrarCamara:
		        img = img[y:y+altura, x:x+anchura]
		
	        # Espejo
		if modoEspejo:
        		img = cv2.flip(img, 1)
		img = cv2.resize(img,(800, 600))
		
		# Calculo de rango de temps
		if rangoDinamico:
		        Tmin = temp_array.min()/100-2
		        Tmax = temp_array.max()/100+2
		else:
		        Tmax = 38
		        Tmin = 24
		        
		
		text = 'Tmin = {:+.1f} Tmax = {:+.1f} FPS = {:.2f}'.format(temp_array.min()/100, temp_array.max()/100, 1/(time.time() - t0))
		cv2.putText(img, text, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
		cv2.imshow('Output', img)
		
		# if 's' is pressed - saving of picture
		key = cv2.waitKey(1) & 0xFF
		if key == ord("s"):
			fname = 'pic_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.jpg'
			cv2.imwrite(fname, img)
			print('Saving image ', fname)
		if key == ord("q"):
		        break
		if key == ord("1"):
		        a = a+incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("2"):
		        a = a-incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("3"):
		        b = b+incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("4"):
		        b = b-incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("7"):
		        c = c+incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("8"):
		        c = c-incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("9"):
		        d = d+incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("0"):
		        d = d-incremento
		        print(a,b,c,d,e,f,g,h)
		        
		if key == ord("z"):
		        e = e+incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("x"):
		        e = e-incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("c"):
		        f = f+incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("v"):
		        f = f-incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("v"):
		        g = g+incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("b"):
		        g = g-incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("n"):
		        h = h+incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("m"):
		        h = h-incremento
		        print(a,b,c,d,e,f,g,h)
		if key == ord("f"):
		        mostrarCamara = not mostrarCamara 
		if key == ord("r"):
		        rangoDinamico = not rangoDinamico
		if key == ord("g"):
		        gaussianEnfoque = not gaussianEnfoque
		if key == ord("e"):
		        modoEspejo = not modoEspejo
		if key == ord("p"):
		        colorMap = (colorMap + 1) % 21
		        print("mapa de color",colorMap  )
		if key == ord("i"):
		        interpolacion = (interpolacion + 1) % 6
		        print("interpolacion", interpolacion)
     
		t0 = time.time()

except KeyboardInterrupt:
	# to terminate the cycle
	ser.write(serial.to_bytes([0xA5,0x35,0x01,0xDB]))
	ser.close()
	cv2.destroyAllWindows()
	print(' Stopped')

# just in case 
ser.close()
cv2.destroyAllWindows()
