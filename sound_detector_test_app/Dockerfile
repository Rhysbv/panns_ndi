FROM python:3.10.13

WORKDIR /usr/src/app

ENV FLASK_APP=app.py

ENV FLASK_RUN_HOST=0.0.0.0

COPY . .

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install avahi-daemon avahi-utils -y

ADD https://downloads.ndi.tv/SDK/NDI_SDK_Linux/Install_NDI_SDK_v6_Linux.tar.gz ./ndi_inst.tar.gz

RUN tar -xvf ndi_inst.tar.gz

RUN yes | ./Install_NDI_SDK_v6_Linux.sh

RUN mkdir $HOME/.ndi

RUN mv ./ndi-config.v1.json $HOME/.ndi/ndi-config.v1.json

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--debug"]