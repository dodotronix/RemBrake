# install all packages on Archlinux

PACKAGE_NAME:=python-adafruit-blinka
PACKAGE_VERSION:="8.47.0"
DOWNLOAD_LINK:="https://aur.archlinux.org/cgit/aur.git/snapshot/${PACKAGE_NAME}.tar.gz"
PKGVER:=$$(echo ${PACKAGE_VERSION} | sed 's/\./\\./g')

all: check_software install_dependencies
	echo ${DOWNLOAD_LINK}
	@wget ${DOWNLOAD_LINK} 
	@tar -xvf ${PACKAGE_NAME}.tar.gz
	@cd ${PACKAGE_NAME}; ls -l; echo ${PKGVER}; \
		sed -i "s/\(pkgver\)=.*/\1=${PKGVER}/" PKGBUILD; \
		sed -i "s/\(arch\)=\([^)]\+\)/\1=\2 'x86_64'/" PKGBUILD; \
		sed -i "s/\(sha256sums\)=.*/\1=('SKIP')/" PKGBUILD; \
		makepkg -si --noconfirm
	@rm -rf ${PACKAGE_NAME}*

check_software:
	echo "TODO is yay installed?"

install_dependencies:
	@sudo pacman -S \
		libusb \
		python-pyftdi \
		--noconfirm
	@yay -S --noconfirm \
		python-sysv_ipc \
		python-adafruit-platformdetect \
		python-gpiod \
		python-adafruit-pureio
