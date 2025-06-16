FROM python:3.10.13

WORKDIR /usr/src/app

COPY . .

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install avahi-daemon avahi-utils -y

ADD https://downloads.ndi.tv/SDK/NDI_SDK_Linux/Install_NDI_SDK_v6_Linux.tar.gz ./ndi_inst.tar.gz

RUN tar -xvf ndi_inst.tar.gz

RUN yes | ./Install_NDI_SDK_v6_Linux.sh

EXPOSE 5959

CMD /usr/src/app/NDI\ SDK\ for\ Linux/bin/x86_64-linux-gnu/ndi-discovery-server