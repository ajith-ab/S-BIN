import RPi.GPIO as GPIO
import os,socket,sys,time

servoPIN = 24 # GPIO 24 for PWM with 50Hz
irPIN = 25 #25 pin for IR sensor

GPIO.setmode(GPIO.BCM)
GPIO.setup(irPIN, GPIO.IN) 

GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) 
p.start(7.5) # Initialization


 
def clientResponse(Ip_addr):
    filename="waste.jpg"
    s = socket.socket()         
    port = 60001              
    s.connect((Ip_addr, port))
    print("Established connection.")
    f=open(filename,"rb")
    data=f.read()
    f.close()
    print("\nSending Length information..")
    length = str(len(data))
    s.send(bytes(length).encode("utf-8"))  
    status=s.recv(2)
    print("Length Reception Acknowledgement - "+str(status.decode("utf-8")))
    print("Sending the image to Amazon Cloud for Tensorflow processing. . .")
    f=open(filename,"rb")
    data=f.read(1)
     # Progress bar to indicate status of sending the image.
    length=int(length)
    count=0
    counter=0
    slab=int(length/10)
    print("\nProgress-")
    while data:
         s.send(data)
         data=f.read(1)
         count+=1
         if count==slab:
             counter+=1
             sys.stdout.write('\r')
             sys.stdout.write('['+"#"*counter+" "*(10-counter)+']'+" "+str(counter*10))
             sys.stdout.flush()
             count=0
    sys.stdout.write("\n")
    sys.stdout.flush()
    print("Sent sucessfully!")
    f.close()
    
    binFlag=s.recv(1)
    print("Cloud response received.")
    if str(binFlag.decode("utf-8"))=="l":
         print("Object is biodegradable. Rotating bin on the left side.")
    elif str(binFlag.decode("utf-8"))=="r":
         print("Object is non-biodegradable. Rotating bin on the right side.")
    s.close()
    os.system("clear")
    return binFlag.decode("utf-8")


def  imageProcessing(Ip_addr):
        try:
           
            binDir=clientResponse(Ip_addr)
            if binDir=='l':
                print("Waste is Biodegradable")
                p.ChangeDutyCycle(2.5)
                time.sleep(1)  
                p.ChangeDutyCycle(7.5)
                time.sleep(1)
                
                
            elif binDir=='r':
                print("Waste is Non-biodegradable")
                p.ChangeDutyCycle(12.5)
                time.sleep(1)  
                p.ChangeDutyCycle(7.5)
                time.sleep(1)
                
            else:
                print("not found in dataset")                  
        except Exception as e:
            print(e)
            pass
        
        
        
if __name__ == "__main__" :
      while True:
          sensor = GPIO.input(25) 
          if sensor==0:  #object was found
               print("Detecting object......") 
               time.sleep(5.0)
               if sensor==0:
                   print("Waste object Was Detected..!")
                   print("taking picture Please Wait...")
                   os.system('fswebcam -r 640X480 -S 15 waste.jpg') # uses Fswebcam to take picture
                   Ip_addr = "ec2-34-229-112-146.compute-1.amazonaws.com" 
                   imageProcessing(Ip_addr)
                   time.sleep(30)
           
          elif sensor==1:
                print("Please place new Waste object")
        
 
                