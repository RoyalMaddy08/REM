# Install Git LFS
!curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
!apt-get install git-lfs
!git lfs install

# Clone repo
!rm REM-xarray -rf
!git clone https://github.com/DahnJ/REM-xarray.git

# Change working directory and install requirements
%cd REM-xarray
!pip install -r requirements.txt
