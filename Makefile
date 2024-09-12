# install all packages on Archlinux

PACKAGE_BLINKA:=python-adafruit-blinka
PACKAGE_PLATFORMDETECT:=python-adafruit-platformdetect
PACKAGE_VERSION_BLINKA:="8.47.0"
PACKAGE_VERSION_PLATFORMDETECT:="3.74.0"
BLINKA_URL:="https://aur.archlinux.org/cgit/aur.git/snapshot/${PACKAGE_BLINKA}.tar.gz"
PLATFORMDETECT_URL="https://aur.archlinux.org/cgit/aur.git/snapshot/${PACKAGE_PLATFORMDETECT}.tar.gz"
PKGVER_BLINKA:=$$(echo ${PACKAGE_VERSION_BLINKA} | sed 's/\./\\./g')
PKGVER_PLATFORMDETECT:=$$(echo ${PACKAGE_VERSION_PLATFORMDETECT} | sed 's/\./\\./g')

all: check_software install_dependencies
	@wget ${PLATFORMDETECT_URL}
	@tar -xvf ${PACKAGE_PLATFORMDETECT}.tar.gz
	@cd ${PACKAGE_PLATFORMDETECT}; \
		sed -i "s/\(pkgver\)=.*/\1=${PKGVER_PLATFORMDETECT}/" PKGBUILD; \
		sed -i "s/\(sha256sums\)=.*/\1=('SKIP')/" PKGBUILD; \
		makepkg -si --noconfirm
	@wget ${BLINKA_URL}
	@tar -xvf ${PACKAGE_BLINKA}.tar.gz
	@cd ${PACKAGE_BLINKA}; \
		sed -i "s/\(pkgver\)=.*/\1=${PKGVER_BLINKA}/" PKGBUILD; \
		sed -i "s/\(arch\)=\([^)]\+\)/\1=\2 'x86_64'/" PKGBUILD; \
		sed -i "s/\(sha256sums\)=.*/\1=('SKIP')/" PKGBUILD; \
		makepkg -si --noconfirm
	@rm -rf ${PACKAGE_BLINKA}*
	@rm -rf ${PACKAGE_PLATFORMDETECT}*

check_software:
	echo "TODO is yay installed?"

install_dependencies:
	@sudo pacman -S \
		libusb \
		python-pyftdi \
		--noconfirm
	@yay -S --noconfirm \
		python-sysv_ipc \
		python-gpiod \
		python-adafruit-pureio
