all: pack

pack:
	cd src/ && zip -r ../brightness.plasmoid .

install: pack
	plasmapkg -r brightness || true
	plasmapkg -i brightness.plasmoid
