#sudo apt update
#sudo apt-get install picamera -y
#sudo pip3 install "picamera[array]" --break-system-packages
sudo apt-get update
sudo apt-get install libraspberrypi0 libraspberrypi-dev libraspberrypi-bin -y
sudo apt full-upgrade -y
sudo apt install -y python3-libcamera python3-kms++ python3-pyqt5
sudo apt install -y python3-picamera2
sudo apt-get -y install python3-pil python3-numpy
sudo pip3 install picamera2 spidev ST7789 --break-system-packages --index-url https://pypi.org/simple
